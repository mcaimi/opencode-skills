---
name: memory-cube
description: >-
  Persistent memory store (~/.memory_cube) that saves conversation knowledge as
  topic-named Markdown files and manages a personality bank for agent tone and
  behavior preferences. Use when the user asks to remember, save, or recall
  information, or asks about a possibly-saved topic. Proactively offer to
  persist behavioral or tone preferences.
license: Apache-2.0
compatibility: Requires python3 and patch (for diff mode)
metadata:
  author: mcaimi
  version: "1.1.0"
allowed-tools: Bash(python3:*) Bash(cat:*) Bash(ls:*) Bash(rm:*) Read Write Edit
---

# Memory Cube

Persistent, topic-organized memory: semantically-named Markdown files with a
YAML frontmatter header (`topic`, `category`, `summary`, `saved_from`).

## Memory Banks

| Bank | Path | Purpose |
|------|------|---------|
| `memory` | `~/.memory_cube/memory` | Factual knowledge: explanations, summaries, decisions, data |
| `personality` | `~/.memory_cube/personality` | Agent tone, mood, specialization, behavioral rules |

Both directories are created automatically on first use.

**Selection rules:**
- `memory` — write **only on explicit user request** ("remember this", "save
  this to memory", "memorize this").
- `personality` — when the user expresses a preference that implies a change in
  agent behavior, **proactively ask** whether to persist it. Do not silently
  store or ignore. Triggers: tone/style ("be more concise", "formal tone"),
  mood ("be friendlier", "add humor"), specialization ("you are a Kubernetes
  expert"), behavioral rules ("run tests before committing", "never use
  emojis"), skill routing ("use git-summary for repo history").

## Command Reference

Scripts live in the skill's `scripts/` directory. Run them from the skill
directory or with their full path.

**List / search memories:**

```bash
python3 scripts/memory-content.py [--search KW] [--bank {memory,personality}] [--format {table,json}] [--limit N]
```

- `--search` matches topic, category, summary, and tags.
- `--limit N` caps rows (default 10).
- `--format json` for machine-readable output.

**Write / update memories:**

```bash
# new or overwrite (heredoc preserves multi-line formatting)
python3 scripts/memorize.py --stdin -o FILE --bank {memory,personality} << 'EOF'
...content...
EOF

# append to existing (start appended content with a blank line or heading;
# the script does not add a separator)
python3 scripts/memorize.py --stdin --append -o FILE --bank {memory,personality} << 'EOF'
...content...
EOF

# apply a unified diff to an existing file
python3 scripts/memorize.py --diff --stdin -o FILE << 'EOF'
--- a/FILE
+++ b/FILE
...
EOF

# copy a local file
python3 scripts/memorize.py -i /path/to/source.md -o FILE

# delete a personality entry
rm ~/.memory_cube/personality/FILE.md
```

Scripts exit non-zero on failure and report the error on stderr.

## File Format

`CATEGORY-SUBTOPIC.md` naming (uppercase, single hyphen) and the required
frontmatter schema are defined in [references/NAMING_AND_FORMAT.md](references/NAMING_AND_FORMAT.md).
Personality files add a `type` field and use the categories `TONE`, `MOOD`,
`SPECIALIZATION`, `RULES`, `SKILLS`, `PREFERENCES`; keep them short and
imperative (a clear rule, not an essay).

## Workflow: Recall

1. **Scan** — `memory-content.py --search "<keyword>"` (most specific term from
   the request; for a broad or ambiguous topic, drop `--search`). Check the
   personality bank with `--bank personality` when relevant.
2. **Present matches** — list matching File/Topic/Summary and ask which to
   load. No matches: answer normally and optionally offer to save the answer.
3. **Load** — read the selected file with `cat` (frontmatter only:
   `head -15`). Prefer stored content as the baseline; supplement if it does
   not cover the query.

## Workflow: Save

Applies to both banks; personality saves are additionally triggered
proactively per the selection rules above.

1. **Determine content** — for a conversation excerpt, synthesize a clean,
   self-contained Markdown document (do not copy raw conversation turns). For
   generic data, format as Markdown where reasonable. Ambiguous request: ask
   what to save.
2. **Choose filename** — user-specified (normalize per NAMING_AND_FORMAT.md)
   or inferred from content. Check for an existing file with the same or a
   similar name (`memory-content.py --search`): prefer **append** when the
   content extends the topic; otherwise overwrite or use a more specific name.
   Personality: first determine the category
   (`TONE`/`MOOD`/`SPECIALIZATION`/`RULES`/`SKILLS`/`PREFERENCES`); if an
   entry overlaps, **replace** (preference superseded), **amend** (new nuance),
   or create a new file (distinct preference).
3. **Write** — use the `--stdin` (or `--append`) commands from the Command
   Reference with the appropriate `--bank`.
4. **Confirm** — report filename, full path, one-line summary, and whether the
   file was created, overwritten, or appended to.

**Personality recall** (at conversation start, or when context suggests it):
scan the personality bank, read entries, and apply them **silently** — do not
list loaded preferences unless asked. Conflicting entries: prefer the most
recently saved; if ambiguous, ask the user.

**Personality update:** modify the existing entry rather than creating a
duplicate; delete the file to revoke a preference.

## Errors, Gotchas, Security

See [references/REFERENCE.md](references/REFERENCE.md). Core points: strip or
mask secrets before saving (warn the user); `-o` must be a plain filename (no
`../`); personality rules that reference skills use the skill's exact name.
