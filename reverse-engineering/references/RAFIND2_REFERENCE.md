# rafind2 Reference

`rafind2` is the command-line front-end for radare2's `r_search` library. It
searches for strings, byte sequences (with optional nibble/bit masks), regular
expressions, numeric values, and ESIL expressions inside a file, a raw block
device, or a directory tree — **without parsing the file format**. This makes
it the right tool when `rabin2 -z` (which only reports strings found inside
known sections) misses data in headers, padding, overlays, or unmapped regions,
or when the file format is unknown/corrupted and full parsing in `r2`/`rabin2`
would fail or be slow.

Source: https://book.rada.re/tools/rafind2/intro.html

## When an agent should reach for rafind2

- Extracting all printable/wide strings from a binary, independent of section
  layout (a `strings`/`rabin2 -z` replacement that also sees data `rabin2`
  would skip).
- Locating a known byte signature, magic number, opcode sequence, or XOR'd
  constant inside a blob when the surrounding structure isn't known yet.
- Grepping for IOCs (URLs, IPs, registry keys, mutex names) embedded in a
  sample during triage, before investing time in full disassembly.
- Finding all occurrences of a crypto constant, API hash, or known shellcode
  stub across a directory of samples.
- Doing a quick file-type identification (`-i`) or file-type carving (`-m`)
  without invoking `rabin2`.
- Confirming a candidate offset found by other means (e.g. `rabin2 -z`) still
  exists after a patch, or finding where to patch a byte pattern (`-R`).

`rafind2` does not disassemble, symbolize, or interpret structure — pair its
offsets with `r2`/`rabin2` (`iS`, `pd`, `px`) to go from "where" to "what".

## Usage Synopsis

```
rafind2 [-mBXnzZhqv] [-a align] [-b sz] [-f/t from/to] [-[e|s|S] str] [-x hex]
        [-R str] [-I str] [-g] -|file|dir ..
```

Use `-` as the filename to read from stdin. Multiple files/directories can be
given; directories are recursed.

## Complete Flag Reference

| Flag | Argument | Description |
|---|---|---|
| `-a` | `align` | Only accept hits aligned to `align` bytes. |
| `-b` | `size` | Set the search block/buffer size (bytes read per chunk). |
| `-B` | — | Use big-endian instead of little-endian (affects `-V`, wide-string reading). |
| `-c` | — | Disable colorful output (mainly affects `-X` hexdump coloring). |
| `-e` | `regex` | Search for regex matches. Can be passed multiple times. |
| `-E` | — | Perform a search using an ESIL expression. |
| `-f` | `from` | Start searching at address/offset `from`. |
| `-F` | `file` | Read the contents of `file` and use it as the search keyword. |
| `-g` | — | Allow the file to grow/resize while replacing (insert mode, used with `-R`). |
| `-h` | — | Show help. |
| `-i` | — | Identify the file type (equivalent to `r2 -nqcpm file`). |
| `-I` | `str` | Filter by `rabin2`-style info (arch/bits/type/...) before searching. |
| `-j` | — | Output results as JSON. |
| `-L` | — | List all IO plugins. |
| `-m` | — | Magic search / file-type carver: scan for embedded file signatures. |
| `-M` | `str` | Set a binary mask (hex) applied on top of the search keyword(s). |
| `-n` | — | Do not stop the search on read errors. |
| `-q` | — | Quiet: suppress filename headings and reduce chatter. |
| `-r` | — | Print hits as radare2 flag/seek commands (`f hitN_M = addr`). |
| `-R` | `str` | Replace every hit with `str`. Prefix selects encoding: `h:` hex, `w:` wide, `s:` string (plain). |
| `-s` | `str` | Search for a literal string. Repeatable for multiple keywords. |
| `-S` | `str` | Search for a literal string encoded as a wide (UTF-16/UCS) string. Input is UTF-8. Repeatable. |
| `-t` | `to` | Stop the search at address/offset `to`. |
| `-v` | — | Print version and exit. |
| `-V` | `size:num[,num2]` | Search for a numeric value (or range) of `size` bytes, honoring endianness (`-B`). E.g. `-V 4:1234` or `-V 4:100,200`. |
| `-x` | `hex` | Search for a hex byte pattern. Supports nibble wildcards with `.` (e.g. `94a2..34`). Repeatable. |
| `-X` | — | Show a hexdump around each search hit instead of a bare offset. |
| `-z` | — | Search for (and list) all zero-terminated ASCII strings — `strings` replacement mode. |
| `-Z` | — | Print the matched string content alongside the offset for any search mode. |

> Flag availability can vary slightly by radare2 build/version; run `rafind2 -h`
> to confirm what the installed build supports before relying on a less common
> flag (`-E`, `-I`, `-V`, `-R`, `-g`, `-L`, `-B`, `-c`).

## Output Modes

By default `rafind2` prints only the **offset** of each hit (one per line,
hex-prefixed, e.g. `0x00000018`). This is intentionally minimal so it can feed
other tools via a shell pipeline. Combine with:

- `-Z` to also print the matched bytes/string next to the offset.
- `-X` to print a hexdump of the surrounding bytes for each hit.
- `-j` to get structured JSON (offset, size, length, type, string, section)
  suitable for programmatic parsing by an agent.
- `-r` to get radare2 commands that create a named flag at each hit, which can
  be piped straight into `r2 -i -`.

## Examples

### String extraction (strings replacement)

Extract every zero-terminated ASCII string in a binary, with content shown:

```bash
rafind2 -zZ /bin/ls
```

Same, but as JSON for programmatic consumption:

```bash
rafind2 -zj /bin/ls
```

Extract strings and grep for embedded URLs (a common IOC-hunting pattern,
catching strings even outside parsed sections that `rabin2 -z` would miss):

```bash
rafind2 -zZ sample.bin | grep -Eo 'https?://[^ ]+'
```

Count how many printable strings a sample contains:

```bash
rafind2 -z sample.bin | wc -l
```

### Literal string / substring search

Find every offset where the literal string `lib` occurs:

```bash
rafind2 -s lib /bin/ls
```

Search for multiple keywords in one pass (repeat `-s`):

```bash
rafind2 -s CreateRemoteThread -s VirtualAllocEx -s WriteProcessMemory malware.exe
```

Search for a wide (UTF-16) string, as commonly embedded by Windows PE binaries:

```bash
rafind2 -S "C:\\Windows\\System32" sample.exe
```

### Byte pattern / opcode / signature search

Search for a raw hex byte sequence (e.g. a NOP sled: `90 90 90`):

```bash
rafind2 -x 909090 shellcode.bin
```

Search for a hex pattern with nibble wildcards (`.` = don't-care nibble) —
useful for matching an instruction encoding while ignoring an immediate/register
field:

```bash
rafind2 -x 94a2..34 firmware.bin
```

Search for several byte signatures at once:

```bash
rafind2 -x 4d5a9000 -x 504b0304 disk.img
```

Apply a binary mask on top of a keyword, to match only specific bits of each
byte (e.g. ignore the low nibble):

```bash
rafind2 -x 6865 -M f0f0 sample.bin
```

### Regex search

Search for a regex pattern (e.g. anything that looks like a domain name):

```bash
rafind2 -e '[a-zA-Z0-9.-]+\.(com|net|org)' -Z sample.bin
```

> Regex support depends on the compiled-in regex backend; if `-e` errors or
> asserts on a given build, fall back to extracting strings with `-zZ` and
> post-filtering with `grep -E` in the shell instead.

### Numeric value search

Find a little-endian 4-byte value (e.g. a magic constant `0x12345678`):

```bash
rafind2 -V 4:305419896 firmware.bin
```

Find all occurrences of a 2-byte value within a range (e.g. port numbers
between 1024 and 2048), big-endian:

```bash
rafind2 -B -V 2:1024,2048 capture.bin
```

### Range-limited search

Restrict the search to an address window, e.g. only the first 0x1000 bytes
(useful to skip a large resource section or focus on a header):

```bash
rafind2 -z -f 0x0 -t 0x1000 sample.bin
```

### Alignment-constrained search

Only report hits aligned on a 4-byte boundary (common for pointers/offsets in
a table):

```bash
rafind2 -x 00000000 -a 4 table.bin
```

### Hexdump context around hits

Show a hexdump of the bytes surrounding each match, instead of just the offset:

```bash
rafind2 -s flag -X ctf_binary
```

### Radare2 command output (chaining into r2)

Emit each hit as an `f` (flag) command and feed it directly into `r2` to
create named flags, then jump to analysis:

```bash
rafind2 -s AES_set_encrypt_key -r sample.bin | r2 -i - -qc 'f~hit' sample.bin
```

Or capture offsets and loop through them with a plain `r2 -c`, printing a
disassembly window at each hit:

```bash
for a in $(rafind2 -s lib /bin/ls); do
  r2 -ns "$a" -qc 'px 32' /bin/ls
done
```

### File type identification and carving

Identify a file's type using radare2's magic database (alternative to `file`):

```bash
rafind2 -i /bin/ls
```

Carve for embedded file signatures inside a blob (e.g. find a ZIP or PNG
hidden inside a firmware dump):

```bash
rafind2 -m firmware.bin
```

### Filtering by binary info before searching

Restrict the search to files matching certain `rabin2`-style info (e.g. only
64-bit ELF binaries in a directory of mixed samples):

```bash
rafind2 -I arch=x86,bits=64 -s "dlopen" ./samples/
```

### Recursive directory search

Search every file under a directory tree for a keyword (e.g. hunting a known
string across a firmware filesystem extraction):

```bash
rafind2 -s "AES_KEY" -q ./firmware_rootfs/
```

### Reading from stdin

Pipe data into `rafind2` by using `-` as the filename, e.g. when searching
inside the output of another extraction tool:

```bash
binwalk -e firmware.bin -O 2>/dev/null; cat firmware.bin.extracted/* | rafind2 -zZ -
```

### Patching / replacing matches (destructive — use with care)

Replace every occurrence of a hex pattern with another hex value in-place.
**This modifies the target file.** Always work on a copy and never run this
against a file the user hasn't explicitly asked to be patched:

```bash
cp sample.bin sample.bin.bak
rafind2 -x deadbeef -R h:cafebabe sample.bin
```

Replace a literal string hit with another string of the same or different
length (`-g` allows the file to grow if the replacement is longer):

```bash
cp sample.bin sample.bin.bak
rafind2 -s "DEBUG_BUILD" -R s:RELEASE_BLD -g sample.bin
```

## Practical Combinations

| Goal | Command |
|---|---|
| Quick triage: dump all strings as JSON | `rafind2 -zj sample.bin` |
| Find all offsets of a magic header anywhere in a blob | `rafind2 -x 7f454c46 blob.bin` |
| Confirm a string exists after patching | `rafind2 -s "new_string" -Z patched.bin` |
| Locate IOC strings across a directory of samples | `rafind2 -s "cmd.exe" -s "powershell" -q ./samples/` |
| Get hex context for manual inspection of a hit | `rafind2 -x 9090 -X sample.bin` |
| Feed hit addresses to r2 for flagging | `rafind2 -s target_str -r sample.bin \| r2 -i -` |

## Notes and Caveats

- Offsets printed by `rafind2` are **physical/raw file offsets** (or virtual
  if the IO layer maps them), not necessarily the same as virtual addresses
  reported by `rabin2`/`r2` once a binary is loaded with its load bias applied
  — double check against `iS`/`ie` in `r2` when correlating.
- `-z` (zero-terminated strings) is intentionally format-agnostic: it finds
  strings wherever they are in the file, including inside headers or unmapped
  padding that `rabin2 -z` (which only looks in known string/data sections)
  will not report. Use both and diff the results when a string is "missing"
  from one.
- `-e` (regex) support and behavior depends on how the local radare2 build was
  compiled; test with a known-good pattern before trusting it for a report.
- `-R`/replace operations are destructive and should only run against a
  disposable copy of the target file, never the original sample.
- `-I` filtering requires radare2 to be able to parse the file header enough
  to extract arch/bits/type info; it will fail or error on corrupted/unknown
  formats — fall back to a plain search without `-I` in that case.
- For very large files, set `-b` to a sensible block size and use `-f`/`-t`
  to window the search instead of scanning the whole file, to keep runtime
  reasonable.
