# Line Counter

A simple, wibe coded cross-platform Python CLI tool that scans a project directory and reports the total lines of code grouped by detected programming language using a colorful Rich table.

## Features

- Recursively walks a target directory
- Ignores common dependency and build folders such as `.git`, `node_modules`, `.venv`, `dist`, and `build`
- Skips binary-like files and non-source text files such as `.txt` and `.log`
- Ignores generated lockfiles and package-manager artifacts such as `package-lock.json` and `yarn.lock`
- Handles files with mixed or invalid encodings safely
- Prints a polished summary table sorted by lines of code
- Includes support for Arduino and Processing source files

## Installation

Install the dependency first:

```bash
pip install rich
```

You can also install from the included requirements file:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with a target directory:

```bash
python main.py /path/to/project/folder
```

Example:

```bash
python main.py .
```

The tool will print a table similar to:

```text
Language    Files    Lines of Code
Python      12       3,421
JavaScript  8        1,204
Markdown    3        240
Grand Total 23       4,865
```

## Notes

- The script is designed to be robust on Windows, macOS, and Linux.
- Permission errors during traversal are skipped silently so the tool can keep going.
- The output is intentionally limited to supported source and documentation file types.
