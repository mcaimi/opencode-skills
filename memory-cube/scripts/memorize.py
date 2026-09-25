#!/usr/bin/env python
#
# Memorize script
# Writes memories into the memory cube
#
# supports these use cases:
# - write a new file to a folder in the memory cube
# - pipes text from stdin to a file in the memory cube
# - applies a diff to a file in the memory cube.
#
# Memory cube paths:
# - MAIN_MEMORY_BANK: default root of the memory cube, located at ~/.memory-cube/memory
# - PERSONALITY_BANK: where the agent/skill updates its own personality, located at ~/.memory-cube/personality
#
# examples:
# 1- write a new file to a folder
#
# ```bash
# # this command copies the input file (-i input.md) to a target file (saved_file.md ) in the MAIN_MEMORY_BANK
# $ memorize.py -i file.md -o saved_file.md
# ```
# 2- pipe text from stdin to a file
#
# ```bash
# # this command receives a chunk of data from stdin and writes it over a file in the MAIN_MEMORY_BANK
# $ echo "${DATA_CHUNK}" | memorize.py --stdin -o saved_file.md
# ```
# ```bash
# # this command receives a chunk of data from stdin and appends it to a file in the MAIN_MEMORY_BANK
# $ echo "${DATA_CHUNK}" | memorize.py --stdin --append -o saved_file.md
#
# 3- apply a diff
#
# ```bash
# # this command reads a diff from a file and applies it to a target file in MAIN_MEMORY_BANK
# $ memorize.py --diff source_chunk.diff -o saved_file.md
#
# ```bash
# # this command reads a diff stdin and applies it to a target file in MAIN_MEMORY_BANK
# $ echo "${DIFF_CHUNK}" | memorize.py --diff --stdin -o saved_file.md
# ```

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
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


def ensure_bank_exists(bank_path: Path) -> None:
    try:
        bank_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"error: permission denied creating directory: {bank_path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"error: cannot create directory {bank_path}: {e}", file=sys.stderr)
        sys.exit(1)


def read_stdin() -> str:
    if sys.stdin.isatty():
        print("error: --stdin specified but no data piped to stdin", file=sys.stderr)
        sys.exit(1)
    try:
        return sys.stdin.read()
    except IOError as e:
        print(f"error: failed to read from stdin: {e}", file=sys.stderr)
        sys.exit(1)


def write_file(target: Path, content: str, append: bool = False) -> None:
    mode = "a" if append else "w"
    try:
        with open(target, mode) as f:
            f.write(content)
    except PermissionError:
        print(f"error: permission denied writing to: {target}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"error: failed to write to {target}: {e}", file=sys.stderr)
        sys.exit(1)


def copy_file(source: Path, target: Path) -> None:
    try:
        shutil.copy2(source, target)
    except PermissionError:
        print(f"error: permission denied copying {source} to {target}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"error: failed to copy {source} to {target}: {e}", file=sys.stderr)
        sys.exit(1)


def apply_diff(target: Path, diff_content: str) -> None:
    try:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".diff", delete=False)
        tmp.write(diff_content)
        tmp_path = tmp.name
        tmp.close()
    except OSError as e:
        print(f"error: failed to create temp file for diff: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            ["patch", str(target), tmp_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"error: patch failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("error: 'patch' command not found, please install it", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"error: failed to run patch: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write memories into the memory cube",
    )
    parser.add_argument(
        "-i", "--input",
        help="Input file to copy into the memory cube",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Target filename within the memory bank",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read content from stdin instead of a file",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to the target file instead of overwriting",
    )
    parser.add_argument(
        "--diff",
        nargs="?",
        const=True,
        default=False,
        help="Apply a unified diff to the target file. "
             "Optionally specify a diff file path; "
             "combine with --stdin to read the diff from stdin",
    )
    parser.add_argument(
        "--bank",
        choices=["memory", "personality"],
        default="memory",
        help="Which memory bank to target (default: memory)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    bank_path = resolve_bank(args.bank)
    ensure_bank_exists(bank_path)
    target = bank_path / args.output

    if args.diff is not False:
        if args.stdin:
            diff_content = read_stdin()
        elif args.diff is not True:
            diff_path = Path(args.diff)
            if not diff_path.is_file():
                print(f"error: diff file not found: {diff_path}", file=sys.stderr)
                sys.exit(1)
            try:
                diff_content = diff_path.read_text()
            except OSError as e:
                print(f"error: cannot read diff file {diff_path}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("error: --diff requires a file path or --stdin", file=sys.stderr)
            sys.exit(1)

        if not target.is_file():
            print(f"error: target file does not exist for patching: {target}", file=sys.stderr)
            sys.exit(1)

        apply_diff(target, diff_content)

    elif args.stdin:
        content = read_stdin()
        write_file(target, content, append=args.append)

    elif args.input:
        source = Path(args.input)
        if not source.is_file():
            print(f"error: input file not found: {source}", file=sys.stderr)
            sys.exit(1)
        if args.append:
            try:
                content = source.read_text()
            except OSError as e:
                print(f"error: cannot read input file {source}: {e}", file=sys.stderr)
                sys.exit(1)
            write_file(target, content, append=True)
        else:
            copy_file(source, target)

    else:
        print("error: specify --input, --stdin, or --diff", file=sys.stderr)
        sys.exit(1)

    print(f"ok: {target}")


if __name__ == "__main__":
    main()
