#!/usr/bin/env python3
"""
Keep only process-error lines and a small amount of context before each match.

Default behavior:
- match lines containing "Process already in progress" (case-insensitive)
- keep the 3 previous lines plus the matching line
- merge overlapping windows

Usage:
    python clean_process_error_context.py path/to/log.txt
    python clean_process_error_context.py path/to/log.txt --before 5
    python clean_process_error_context.py path/to/log.txt --pattern "process error"
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_PATTERN = r"Process already in progress"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Keep only log lines matching a process-error pattern plus a number of "
            "previous context lines."
        )
    )
    parser.add_argument("input_file", help="Path to the source log file")
    parser.add_argument(
        "--before",
        type=int,
        default=3,
        help="How many lines before each match to keep (default: 3)",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help='Case-insensitive regex used to detect matching lines (default: "Process already in progress")',
    )
    return parser.parse_args()


def collect_kept_indexes(lines: list[str], pattern: re.Pattern[str], before: int) -> list[int]:
    kept_indexes: set[int] = set()
    for index, line in enumerate(lines):
        if not pattern.search(line):
            continue
        start = max(0, index - before)
        kept_indexes.update(range(start, index + 1))
    return sorted(kept_indexes)


def build_output_path(input_path: Path) -> Path:
    return Path.cwd() / f"{input_path.stem}_process_error_context.txt"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        return 1

    if args.before < 0:
        print("--before must be >= 0", file=sys.stderr)
        return 1

    try:
        pattern = re.compile(args.pattern, re.IGNORECASE)
    except re.error as exc:
        print(f"Invalid regex for --pattern: {exc}", file=sys.stderr)
        return 1

    lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines()
    matched_indexes = [index for index, line in enumerate(lines) if pattern.search(line)]
    kept_indexes = collect_kept_indexes(lines, pattern, args.before)
    kept_lines = [lines[index] for index in kept_indexes]

    output_path = build_output_path(input_path)
    output_text = "\n".join(kept_lines)
    if kept_lines:
        output_text += "\n"
    output_path.write_text(output_text, encoding="utf-8")

    print(f"Input lines:     {len(lines)}")
    print(f"Matched lines:   {len(matched_indexes)}")
    print(f"Context before:  {args.before}")
    print(f"Kept lines:      {len(kept_lines)}")
    print(f"Output file:     {output_path}")

    if matched_indexes:
        print(
            "Matched line nos:"
            f" {', '.join(str(index + 1) for index in matched_indexes[:20])}"
            + (" ..." if len(matched_indexes) > 20 else "")
        )
    else:
        print("Matched line nos: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
