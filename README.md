# Password Generator

A small, dependency-free password generator written in pure Python.
Use it from the terminal or through a simple desktop window.

- Choose character sets: digits, uppercase letters, lowercase letters, special characters (`% * ) ? @ # $ ~`)
- Every password contains at least one character from each selected set
- Set the password length (default: 8) and how many passwords to generate (default: 5)
- Uses the [`secrets`](https://docs.python.org/3/library/secrets.html) module, which is designed for generating secure passwords
- No third-party packages, only the Python standard library

## Requirements

| Mode | Python | Notes |
|---|---|---|
| Command line | 3.9+ | Standard library only |
| Desktop window | 3.10+ | Needs `tkinter` (see below) |

`tkinter` ships with the python.org installers for macOS and Windows.
Some distributions package it separately:

```sh
brew install python-tk@3.15        # macOS, Homebrew (match your Python version)
sudo apt install python3-tk        # Debian / Ubuntu
sudo dnf install python3-tkinter   # Fedora
```

Check that it is available:

```sh
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

## Command line

```sh
python3 passgen.py [options]
```

| Option | Description |
|---|---|
| `-d`, `--digits` | Include digits |
| `-u`, `--upper` | Include uppercase letters |
| `-w`, `--lower` | Include lowercase letters |
| `-s`, `--special` | Include special characters `%*)?@#$~` |
| `-l`, `--length N` | Password length (default: 8) |
| `-n`, `--count N` | Number of passwords (default: 5) |
| `-h`, `--help` | Show help |

If no character set is selected, all four are used.
The length must be at least the number of selected sets.

### Examples

```sh
# 5 passwords of 8 characters, all character sets
python3 passgen.py

# 3 passwords of 16 characters, letters and digits only
python3 passgen.py -u -w -d -l 16 -n 3

# A 6-digit PIN
python3 passgen.py -d -l 6 -n 1

# Save 20 passwords to a file
python3 passgen.py -l 12 -n 20 > passwords.txt
```

## Desktop window

```sh
python3 passgen_gui.py
```

- Toggle character sets and set the length (1–128) and count (1–100)
- **Generate** (or press <kbd>Enter</kbd>) creates a new list
- **Copy** next to each password copies just that one; **Copy all** copies the whole list
- **Save to file…** (or <kbd>⌘</kbd>+<kbd>S</kbd> on macOS) writes all passwords to a text file, one per line
- Switch the interface language between **English**, **Русский** and **Srpski** from the drop-down in the top-right corner

The selected language is remembered in:

- macOS: `~/Library/Application Support/passgen/settings.json`
- Linux / other: `~/.config/passgen/settings.json`

English is used when no setting has been saved yet.

## Project structure

```
passgen.py       # Password generation logic and the command-line interface
passgen_gui.py   # Desktop window (tkinter)
i18n.py          # Interface translations
```

## Adding a language

Open `i18n.py`, add the language to `LANGUAGES`, and add a dictionary to `STRINGS`
with the same keys as the existing ones:

```python
LANGUAGES = {"en": "English", "ru": "Русский", "sr": "Srpski", "de": "Deutsch"}

STRINGS = {
    ...
    "de": {
        "title": "Passwortgenerator",
        "generate": "Generieren",
        ...
    },
}
```

The window size adjusts automatically to fit the longest translation.

## License

[MIT](LICENSE)
