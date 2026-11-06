#!/usr/bin/env python3
"""Простой генератор паролей."""

import argparse
import secrets
import string
import sys
from pathlib import Path

# В сборке PyInstaller файлы лежат во временной папке sys._MEIPASS, иначе — рядом со скриптом
APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def read_version() -> str:
    """Номер версии из файла VERSION — единственного места, где он задаётся."""
    try:
        return (APP_DIR / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


VERSION = read_version()

CHARSETS = {
    "digits": string.digits,
    "upper": string.ascii_uppercase,
    "lower": string.ascii_lowercase,
    "special": "%*)?@#$~",
}


def generate_password(length: int, sets: list[str]) -> str:
    # По одному символу из каждого выбранного набора, чтобы все они точно были в пароле
    chars = [secrets.choice(s) for s in sets]
    pool = "".join(sets)
    chars += [secrets.choice(pool) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Генератор паролей. Если не выбран ни один набор символов, используются все."
    )
    parser.add_argument("-d", "--digits", action="store_true", help="цифры")
    parser.add_argument("-u", "--upper", action="store_true", help="прописные буквы")
    parser.add_argument("-w", "--lower", action="store_true", help="строчные буквы")
    parser.add_argument("-s", "--special", action="store_true", help="спецсимволы %%*)?@#$~")
    parser.add_argument("-l", "--length", type=int, default=8, help="длина пароля (по умолчанию 8)")
    parser.add_argument("-n", "--count", type=int, default=5, help="количество паролей (по умолчанию 5)")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")
    args = parser.parse_args()

    sets = [chars for name, chars in CHARSETS.items() if getattr(args, name)]
    if not sets:
        sets = list(CHARSETS.values())

    if args.count < 1:
        parser.error("количество паролей должно быть не меньше 1")
    if args.length < len(sets):
        parser.error(f"длина пароля должна быть не меньше {len(sets)} (по символу из каждого набора)")

    for _ in range(args.count):
        print(generate_password(args.length, sets))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
