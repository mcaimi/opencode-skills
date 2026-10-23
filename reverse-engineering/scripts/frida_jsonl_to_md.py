#!/usr/bin/env python3
"""Parse Frida agent JSON-lines send() output into a structured Markdown report."""

import json
import sys


def parse_jsonl(source):
    """Read JSON-lines from a file-like object, grouping by 'type'. Skips malformed lines."""
    groups = {}
    skipped = 0

    for line in source:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(obj, dict):
            skipped += 1
            continue

        event_type = obj.get("type", "unknown")
        groups.setdefault(event_type, []).append(obj)

    return groups, skipped


def render_markdown(groups):
    """Render grouped events as one Markdown table per event type."""
    lines = []

    for event_type in sorted(groups):
        entries = groups[event_type]
        columns = []
        for entry in entries:
            for key in entry:
                if key not in columns:
                    columns.append(key)

        lines.append(f"## {event_type} ({len(entries)})")
        lines.append("")
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("|" + "|".join(["---"] * len(columns)) + "|")
        for entry in entries:
            row = [str(entry.get(col, "")) for col in columns]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <frida-jsonl-file-or-'-'>", file=sys.stderr)
        print("  Pass '-' to read from stdin.", file=sys.stderr)
        sys.exit(1)

    try:
        if sys.argv[1] == "-":
            groups, skipped = parse_jsonl(sys.stdin)
        else:
            with open(sys.argv[1], "r") as f:
                groups, skipped = parse_jsonl(f)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)

    if not groups:
        print("No valid JSON-lines events found in input.", file=sys.stderr)
        sys.exit(1)

    if skipped:
        print(f"Warning: skipped {skipped} malformed line(s).", file=sys.stderr)

    print(render_markdown(groups))
