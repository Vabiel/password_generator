#!/usr/bin/env python3
"""Графический интерфейс генератора паролей (tkinter, без зависимостей)."""

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font, ttk

from i18n import DEFAULT_LANGUAGE, LANGUAGES, STRINGS
from passgen import CHARSETS, generate_password

FONT_SIZE = 14
MONO = ("Menlo", FONT_SIZE)

if sys.platform == "darwin":
    SETTINGS_FILE = Path.home() / "Library/Application Support/passgen/settings.json"
else:
    SETTINGS_FILE = Path.home() / ".config/passgen/settings.json"


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict) -> None:
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass  # Не смогли запомнить язык — не повод мешать работе


class ScrollFrame(ttk.Frame):
    """Прокручиваемая область: строки кладутся в self.inner."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.canvas = tk.Canvas(self, highlightthickness=0, height=240)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.inner = ttk.Frame(self.canvas)
        self.inner.columnconfigure(1, weight=1)
        window = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")

        # Внутренняя рамка растягивается по ширине холста, область прокрутки — по содержимому
        self.inner.bind(
            "<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))

        # Колесо мыши работает, только когда курсор над списком
        self.bind("<Enter>", lambda _e: self.bind_all("<MouseWheel>", self._on_wheel))
        self.bind("<Leave>", lambda _e: self.unbind_all("<MouseWheel>"))

    def _on_wheel(self, event: tk.Event) -> None:
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def clear(self) -> None:
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


class App(ttk.Frame):
    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root, padding=14)
        self.root = root
        self.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        for name in ("TkDefaultFont", "TkTextFont"):
            font.nametofont(name).configure(size=FONT_SIZE)
        ttk.Style().configure("TLabelframe.Label", font=("TkDefaultFont", FONT_SIZE, "bold"))

        self.settings = load_settings()
        lang = self.settings.get("language")
        self.lang = lang if lang in STRINGS else DEFAULT_LANGUAGE

        # Элементы, у которых меняется текст при смене языка: (виджет, ключ перевода)
        self.translatable: list[tuple[tk.Misc, str]] = []
        self.status_msg: tuple[str, dict] | None = None  # ключ + параметры, чтобы переводить и статус
        self.passwords: list[str] = []
        self.copy_buttons: list[ttk.Button] = []

        self.flags = {name: tk.BooleanVar(value=True) for name in CHARSETS}
        self.length = tk.IntVar(value=8)
        self.count = tk.IntVar(value=5)
        self.status = tk.StringVar()

        self._build_language_bar()
        self._build_settings()
        self._build_buttons()

        self.list = ScrollFrame(self)
        self.list.grid(row=3, column=0, sticky="nsew")
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

        status_label = ttk.Label(self, textvariable=self.status, foreground="gray", anchor="w")
        status_label.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        # Длинное сообщение (например, путь к файлу) переносится, а не раздвигает окно
        self.bind("<Configure>", lambda e: status_label.configure(wraplength=e.width - 28))

        root.bind("<Return>", lambda _e: self.generate())
        root.bind("<Command-s>", lambda _e: self.save())
        self._fix_window_size()
        self.apply_language()
        self.generate()

    def _fix_window_size(self) -> None:
        """Задаёт размер окна по самому широкому языку, чтобы оно не прыгало при переключении."""
        current = self.lang
        width = height = 0
        for code in STRINGS:
            self.lang = code
            self.apply_language()
            self.root.update_idletasks()
            width = max(width, self.root.winfo_reqwidth())
            height = max(height, self.root.winfo_reqheight())
        self.lang = current
        self.root.minsize(width, height)
        # Явно заданный размер отключает автоподстройку окна под содержимое
        self.root.geometry(f"{width}x{height}")

    # --- построение интерфейса ---

    def _tr(self, widget: tk.Misc, key: str) -> tk.Misc:
        self.translatable.append((widget, key))
        return widget

    def _build_language_bar(self) -> None:
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="e", pady=(0, 8))
        self._tr(ttk.Label(bar, padding=(0, 0, 6, 0)), "language").pack(side="left")
        self.lang_box = ttk.Combobox(
            bar, state="readonly", values=list(LANGUAGES.values()), width=9
        )
        self.lang_box.set(LANGUAGES[self.lang])
        self.lang_box.bind("<<ComboboxSelected>>", self._on_language_selected)
        self.lang_box.pack(side="left")

    def _build_settings(self) -> None:
        box = self._tr(ttk.LabelFrame(self, padding=(12, 8)), "settings")
        box.grid(row=1, column=0, sticky="ew")
        box.columnconfigure(1, weight=1)

        for i, name in enumerate(CHARSETS):
            self._tr(ttk.Checkbutton(box, variable=self.flags[name]), name).grid(
                row=i, column=0, columnspan=2, sticky="w", pady=2
            )

        ttk.Separator(box).grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

        # Разрешаем вводить только цифры (пустое поле допустимо, пока пользователь печатает)
        only_digits = (self.register(lambda s: s == "" or (s.isdigit() and len(s) <= 3)), "%P")
        fields = [("length", self.length, 128), ("count", self.count, 100)]
        # Подпись над полем: поле всегда стоит на одном месте, какой бы длины ни был перевод
        for i, (key, var, top) in enumerate(fields):
            row = 5 + i * 2
            self._tr(ttk.Label(box), key).grid(
                row=row, column=0, columnspan=2, sticky="w", pady=(8 if i else 0, 2)
            )
            ttk.Spinbox(
                box, from_=1, to=top, textvariable=var, width=6,
                validate="key", validatecommand=only_digits,
            ).grid(row=row + 1, column=0, columnspan=2, sticky="w")

    def _build_buttons(self) -> None:
        bar = ttk.Frame(self)
        bar.grid(row=2, column=0, sticky="ew", pady=10)
        self._tr(ttk.Button(bar, command=self.generate), "generate").pack(side="left")
        self._tr(ttk.Button(bar, command=self.copy_all), "copy_all").pack(side="left", padx=6)
        self._tr(ttk.Button(bar, command=self.save), "save").pack(side="left")

    # --- язык ---

    def t(self, key: str, **kwargs) -> str:
        return STRINGS[self.lang][key].format(**kwargs)

    def _on_language_selected(self, _event: tk.Event) -> None:
        name = self.lang_box.get()
        self.lang = next(code for code, title in LANGUAGES.items() if title == name)
        self.lang_box.selection_clear()
        self.settings["language"] = self.lang
        save_settings(self.settings)
        self.apply_language()

    def apply_language(self) -> None:
        self.root.title(self.t("title"))
        for widget, key in self.translatable:
            widget.configure(text=self.t(key))
        for button in self.copy_buttons:
            button.configure(text=self.t("copy"))
        if self.status_msg:
            self.set_status(*self.status_msg)

    def set_status(self, key: str | None, params: dict | None = None) -> None:
        self.status_msg = (key, params or {}) if key else None
        self.status.set(self.t(key, **(params or {})) if key else "")

    # --- действия ---

    def generate(self) -> None:
        sets = [CHARSETS[name] for name, var in self.flags.items() if var.get()]
        try:
            length, count = self.length.get(), self.count.get()
        except tk.TclError:
            return self.set_status("err_empty")
        if not sets:
            return self.set_status("err_sets")
        if not 1 <= count <= 100:
            return self.set_status("err_count")
        if not len(sets) <= length <= 128:
            return self.set_status("err_length", {"min": len(sets)})

        self.passwords = [generate_password(length, sets) for _ in range(count)]
        self.list.clear()
        self.copy_buttons = [self._add_row(i, p) for i, p in enumerate(self.passwords)]
        self.set_status(None)

    def _add_row(self, i: int, password: str) -> ttk.Button:
        ttk.Label(self.list.inner, text=f"{i + 1}.", width=4, anchor="e").grid(
            row=i, column=0, padx=(0, 6)
        )
        # Поле только для чтения: пароль можно выделить мышью, но не изменить
        entry = ttk.Entry(self.list.inner, font=MONO)
        entry.insert(0, password)
        entry.configure(state="readonly")
        entry.grid(row=i, column=1, sticky="ew", pady=2)
        button = ttk.Button(self.list.inner, text=self.t("copy"), width=11)
        button.configure(command=lambda: self._copy_one(password, button))
        button.grid(row=i, column=2, padx=(6, 2))
        return button

    def _set_clipboard(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)

    def _copy_one(self, password: str, button: ttk.Button) -> None:
        self._set_clipboard(password)
        button.configure(text=self.t("copied"))
        # Возвращаем подпись на текущем языке — он мог смениться за это время
        button.after(1200, lambda: button.winfo_exists() and button.configure(text=self.t("copy")))

    def copy_all(self) -> None:
        if not self.passwords:
            return
        self._set_clipboard("\n".join(self.passwords))
        self.set_status("copied_all", {"n": len(self.passwords)})

    def save(self) -> None:
        if not self.passwords:
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title=self.t("save_title"),
            initialfile="passwords.txt",
            defaultextension=".txt",
            filetypes=[(self.t("txt_file"), "*.txt"), (self.t("all_files"), "*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.passwords) + "\n")
        except OSError as e:
            return self.set_status("save_failed", {"err": e.strerror})
        self.set_status("saved", {"path": path})


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
