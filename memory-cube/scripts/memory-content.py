#!/usr/bin/env python
#
# Memory Content Scanner
# Scans the memory cube and returns a table of files with their frontmatter metadata.
#
# examples:
#
# ```bash
# # list all memories in the default bank (memory)
# $ memory-content.py
# ```
# ```bash
# # list all memories in the personality bank
# $ memory-content.py --bank personality
# ```
# ```bash
# # search for memories matching a keyword in topic, category, summary, or tags
# $ memory-content.py --search "attention"
# ```
# ```bash
# # output as JSON instead of a table
# $ memory-content.py --format json
# ```

import argparse
import json
import sys
from pathlib import Path

MAIN_MEMORY_BANK: str = "~/.memory_cube/memory"
PERSONALITY_BANK: str = "~/.memory_cube/personality"


def resolve_bank(bank_name: str) -> Path:
    banks = {
        "memory": MAIN_MEMORY_BANK,
        "personality": PERSONALITY_BANK,
    }
    raw = banks.get(bank_name, MAIN_MEMORY_BANK)
    return Path(raw).expanduser()


def parse_frontmatter(filepath: Path) -> dict | None:
    try:
        text = filepath.read_text()
    except OSError as e:
        print(f"warning: cannot read {filepath}: {e}", file=sys.stderr)
        return None

    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return None

    end = stripped.find("---", 3)
    if end == -1:
        return None

    block = stripped[3:end].strip()
    meta = {}
    current_key = None
    current_list = None

    for line in block.splitlines():
        if not line.strip():
            continue

        if line.startswith("  - ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(line.strip().lstrip("- "))
            meta[current_key] = current_list
            continue

        if current_list is not None:
            current_list = None

        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            current_key = key
            if val:
                meta[key] = val
            else:
                current_list = []
        else:
            current_key = None

    return meta


def matches_search(meta: dict, query: str) -> bool:
    query_lower = query.lower()
    for val in meta.values():
        if isinstance(val, str) and query_lower in val.lower():
            return True
        if isinstance(val, list):
            for item in val:
                if query_lower in str(item).lower():
                    return True
    return False


def scan_bank(bank_path: Path, search: str | None = None) -> list[dict]:
    if not bank_path.is_dir():
        return []

    results = []
    try:
        files = sorted(bank_path.glob("*.md"))
    except OSError as e:
        print(f"error: cannot scan {bank_path}: {e}", file=sys.stderr)
        sys.exit(1)

    for f in files:
        meta = parse_frontmatter(f)
        entry = {
            "file": f.name,
            "topic": meta.get("topic", "") if meta else "",
            "category": meta.get("category", "") if meta else "",
            "summary": meta.get("summary", "") if meta else "",
            "saved_from": meta.get("saved_from", "") if meta else "",
            "tags": meta.get("tags", []) if meta else [],
        }

        if search and meta:
            if not matches_search(meta, search):
                continue
        elif search and not meta:
            if search.lower() not in f.name.lower():
                continue

        results.append(entry)

    return results


def format_table(entries: list[dict]) -> str:
    if not entries:
        return "No memories found."

    h_file = "File"
    h_topic = "Topic"
    h_category = "Category"
    h_summary = "Summary"

    w_file = max(len(h_file), *(len(e["file"]) for e in entries))
    w_topic = max(len(h_topic), *(len(e["topic"]) for e in entries))
    w_cat = max(len(h_category), *(len(e["category"]) for e in entries))
    w_sum = max(len(h_summary), *(len(e["summary"]) for e in entries))

    header = (
        f"| {h_file:<{w_file}} "
        f"| {h_topic:<{w_topic}} "
        f"| {h_category:<{w_cat}} "
        f"| {h_summary:<{w_sum}} |"
    )
    sep = (
        f"| {'-' * w_file} "
        f"| {'-' * w_topic} "
        f"| {'-' * w_cat} "
        f"| {'-' * w_sum} |"
    )

    rows = []
    for e in entries:
        row = (
            f"| {e['file']:<{w_file}} "
            f"| {e['topic']:<{w_topic}} "
            f"| {e['category']:<{w_cat}} "
            f"| {e['summary']:<{w_sum}} |"
        )
        rows.append(row)

    return "\n".join([header, sep, *rows])


def format_json(entries: list[dict]) -> str:
    return json.dumps(entries, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan the memory cube and list stored memories with their metadata",
    )
    parser.add_argument(
        "--bank",
        choices=["memory", "personality"],
        default="memory",
        help="Which memory bank to scan (default: memory)",
    )
    parser.add_argument(
        "--search",
        default=None,
        help="Filter memories by keyword (matches topic, category, summary, and tags)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        dest="output_format",
        help="Output format (default: table)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    bank_path = resolve_bank(args.bank)

    if not bank_path.is_dir():
        print(f"No memories found. Bank directory does not exist: {bank_path}")
        sys.exit(0)

    entries = scan_bank(bank_path, search=args.search)

    if args.output_format == "json":
        print(format_json(entries))
    else:
        print(format_table(entries))


if __name__ == "__main__":
    main()
