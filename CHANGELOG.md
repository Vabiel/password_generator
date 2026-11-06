# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `--version` option for the command line; the version is also shown in the window title
- The version number is kept in a single `VERSION` file; the release build fails if the tag does not match it

## [1.0.0] - 2026-11-06

### Added

- Command-line generator (`passgen.py`): choose digits, uppercase, lowercase and special characters,
  password length (default 8) and number of passwords (default 5)
- Every password contains at least one character from each selected set; uses the `secrets` module
- Desktop window (`passgen_gui.py`) built with tkinter, no third-party dependencies
- Copy button for each password, **Copy all**, and **Save to file…** (⌘S / Ctrl+S)
- Interface in English, Russian and Serbian (Latin); the selected language is remembered between runs
- App icon
- Ready-to-run apps for macOS (Apple Silicon), Windows and Linux, built by GitHub Actions on each version tag

[Unreleased]: https://github.com/Vabiel/password_generator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Vabiel/password_generator/releases/tag/v1.0.0
