# Run: pip install rich before executing this script.

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Iterator

try:
    from rich.console import Console
    from rich.table import Table
except ImportError as exc:  # pragma: no cover - handled at runtime
    print("rich is required. Install it with: pip install rich", file=sys.stderr)
    raise SystemExit(1) from exc

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".next",
}

LANGUAGE_BY_EXTENSION = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".java": "Java",
    ".ino": "Arduino",
    ".pde": "Processing",
    ".pyde": "Processing",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".c": "C",
    ".h": "C/C++",
    ".cpp": "C/C++",
    ".cc": "C/C++",
    ".cxx": "C/C++",
    ".hpp": "C/C++",
    ".hh": "C/C++",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
    ".lua": "Lua",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "INI",
    ".md": "Markdown",
    ".rst": "reStructuredText",
}

LANGUAGE_COLORS = {
    "Python": "cyan",
    "JavaScript": "yellow",
    "TypeScript": "magenta",
    "HTML": "green",
    "CSS": "bright_blue",
    "Java": "red",
    "Arduino": "bright_magenta",
    "Processing": "bright_blue",
    "C/C++": "white",
    "Go": "bright_green",
    "Rust": "bright_red",
    "Markdown": "bright_magenta",
    "Shell": "bright_cyan",
    "default": "white",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Count lines of code in a project directory and summarize them by language."
    )
    parser.add_argument("target_dir", help="Path to the project directory to scan")
    return parser.parse_args()


def should_skip_directory(path: Path) -> bool:
    """Return True when a directory should be skipped."""
    return path.name in SKIP_DIRS or path.name.startswith(".")


def detect_language(path: Path) -> str | None:
    """Return the programming language for a file based on its extension."""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".log"}:
        return None
    return LANGUAGE_BY_EXTENSION.get(suffix)


def is_probably_binary(path: Path) -> bool:
    """Return True for files that appear to be binary."""
    try:
        with path.open("rb") as handle:
            chunk = handle.read(1024)
    except (PermissionError, OSError):
        return True

    return b"\x00" in chunk


def count_lines(text: str) -> int:
    """Count logical lines in a text blob."""
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def walk_project(root: Path) -> Iterator[Path]:
    """Yield files under a project directory while skipping excluded paths."""
    try:
        entries = list(root.iterdir())
    except (PermissionError, OSError):
        return

    for entry in entries:
        try:
            if entry.is_dir():
                if should_skip_directory(entry):
                    continue
                yield from walk_project(entry)
            elif entry.is_file():
                yield entry
        except (PermissionError, OSError):
            continue


def collect_statistics(root: Path) -> tuple[DefaultDict[str, int], DefaultDict[str, int], int]:
    """Collect per-language file counts, line counts, and the grand total."""
    file_counts: DefaultDict[str, int] = defaultdict(int)
    line_counts: DefaultDict[str, int] = defaultdict(int)
    total_lines = 0

    for path in walk_project(root):
        language = detect_language(path)
        if not language:
            continue

        if is_probably_binary(path):
            continue

        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        except (PermissionError, OSError, UnicodeError):
            continue

        line_total = count_lines(text)
        file_counts[language] += 1
        line_counts[language] += line_total
        total_lines += line_total

    return file_counts, line_counts, total_lines


def print_summary(root: Path, file_counts: DefaultDict[str, int], line_counts: DefaultDict[str, int], total_lines: int) -> None:
    """Render a colorful Rich table for the collected statistics."""
    console = Console()
    table = Table(
        title=f"Lines of Code Summary: {root}",
        header_style="bold cyan",
        title_style="bold magenta",
    )
    table.add_column("Language", style="bold", no_wrap=True)
    table.add_column("Files", justify="right", style="cyan")
    table.add_column("Lines of Code", justify="right", style="green")

    rows = sorted(line_counts.items(), key=lambda item: item[1], reverse=True)
    if not rows:
        table.add_row("No supported files found", "0", "0", style="yellow")
    else:
        for language, line_total in rows:
            table.add_row(
                language,
                str(file_counts.get(language, 0)),
                f"{line_total:,}",
                style=LANGUAGE_COLORS.get(language, LANGUAGE_COLORS["default"]),
            )

        table.add_row(
            "Grand Total",
            str(sum(file_counts.values())),
            f"{total_lines:,}",
            style="bold bright_yellow",
        )

    console.print(table)


def main() -> int:
    """Run the CLI entry point."""
    args = parse_args()
    target_path = Path(args.target_dir).expanduser()

    if not target_path.exists():
        print(f"Error: path does not exist: {target_path}", file=sys.stderr)
        return 1

    if not target_path.is_dir():
        print(f"Error: path is not a directory: {target_path}", file=sys.stderr)
        return 1

    root = target_path.resolve()
    file_counts, line_counts, total_lines = collect_statistics(root)
    print_summary(root, file_counts, line_counts, total_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
