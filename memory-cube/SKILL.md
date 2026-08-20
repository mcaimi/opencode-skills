---
name: memory-cube
description: >-
  Persistent memory store for conversation knowledge. Saves topic explanations,
  technical summaries, decisions, and arbitrary data as semantically-named
  Markdown files in a local memory cube (~/.memory_cube). Use when the user asks
  to remember, save, memorize, or store information from the current conversation
  or from external content. Also use when the user asks about a topic that may
  have been previously saved — scan the memory cube for matching memories and
  offer to load them. Supports writing new memories, appending to existing ones,
  patching memories with diffs, and recalling stored memories by topic. Files are
  named after their semantic content (e.g. MACHINE_LEARNING-ATTENTION_MECHANISM.md)
  so they can be recalled by topic. Also manages a personality bank for agent
  interaction preferences (tone, mood, specialization) and behavioral rules
  (skill routing, workflow constraints). When the user adjusts agent behavior or
  tone, proactively offer to persist the preference in the personality bank.
license: Apache-2.0
compatibility: Requires python3 and patch (for diff mode)
metadata:
  author: mcaimi
  version: "1.0.0"
allowed-tools: Bash(python3:*) Bash(cat:*) Bash(ls:*) Bash(rm:*) Read Write Edit
---

# Memory Cube

Save conversation knowledge and arbitrary data as semantically-named Markdown
files in a persistent, topic-organized memory store.

## Memory Banks

| Bank          | Path                       | Purpose                                |
|---------------|----------------------------|----------------------------------------|
| `memory`      | `~/.memory_cube/memory`    | General knowledge, topics, summaries   |
| `personality`  | `~/.memory_cube/personality`| Agent tone, mood, specialization, and behavioral rules |

Both directories are created automatically on first use.

### Bank Selection Rules

The two banks serve fundamentally different purposes and have different
triggering rules:

- **`memory` bank** — Stores factual knowledge: topic explanations, technical
  summaries, decisions, data. The user must **explicitly request** saving
  content to this bank (e.g., "remember this", "save this to memory",
  "memorize this explanation"). Never write to the memory bank unless asked.

- **`personality` bank** — Stores interaction preferences and behavioral rules
  that shape how the agent works. When the user says something that implies a
  change in agent behavior, tone, or workflow, **proactively ask** whether they
  want to persist it in the personality bank. Do not silently store or silently
  ignore — always ask first.

#### Personality Bank Trigger Examples

Proactively offer to save to the personality bank when the user:

- Adjusts tone or style: "be more concise", "use a formal tone", "talk to me
  like a senior engineer", "stop being so verbose"
- Sets mood or demeanor: "be friendlier", "keep it professional", "add some
  humor"
- Defines a specialization: "you are a Kubernetes expert", "focus on security",
  "act as a data engineer"
- Establishes a behavioral rule: "always use the security-auditor skill when I
  ask about vulnerabilities", "run tests before committing", "never use emojis"
- Assigns skill routing: "use the git-summary skill whenever I ask about repo
  history", "for Wikipedia lookups use the wikipedia skill"

When you detect one of these triggers, respond with something like:

> Got it, I'll adjust. Would you like me to save this preference to the
> personality bank so it persists across conversations?

If the user confirms, save it. If they decline, apply the preference for the
current conversation only.

## Input Parameters

### Required

- `content` (string): The information to save. Either extracted from the current
  conversation or provided directly by the user. If the user asks to save a
  portion of the conversation, synthesize the relevant content into a clean
  Markdown document before writing.

### Optional

| Parameter   | Default    | Notes                                                            |
|-------------|------------|------------------------------------------------------------------|
| `topic`     | inferred   | Semantic topic name; inferred from content if not specified      |
| `bank`      | `"memory"` | `"memory"` or `"personality"`                                    |
| `append`    | `false`    | Append to an existing memory file instead of overwriting         |
| `diff`      | `null`     | A unified diff to apply to an existing memory file               |

## File Naming and Content Format

Files use a `CATEGORY-SUBTOPIC.md` naming convention with uppercase and
underscores. Every file must start with a YAML frontmatter metadata header
(`topic`, `category`, `summary`, `saved_from`).

Read [the naming and format guide](references/NAMING_AND_FORMAT.md) for the
full convention, metadata header schema, and content formatting rules.

## Available Scripts

- **`scripts/memorize.py`** — Writes content into the memory cube. Supports
  three modes: file copy (`-i`), stdin pipe (`--stdin`), and diff patching
  (`--diff`). Targets a bank with `--bank`. Append mode with `--append`.
- **`scripts/memory-content.py`** — Scans a memory bank and lists all stored
  memories with their frontmatter metadata. Supports `--search` to filter by
  keyword (matches topic, category, summary, and tags), `--bank` to select
  which bank to scan, and `--format` for table or JSON output.

## Workflow: Recall

When the user asks about a topic that may have been previously discussed or
saved, check the memory cube before answering from scratch.

### Step 1: Scan the memory cube

Run `memory-content.py` with a search keyword derived from the user's question:

```bash
python3 scripts/memory-content.py --search "<keyword>" --format json
```

Extract the keyword from the user's request. Use the most specific term — for
example, if the user asks "what did we say about the attention mechanism?", search
for `"attention"`.

If the topic is broad or ambiguous, run a second scan without `--search` to list
all available memories and match manually:

```bash
python3 scripts/memory-content.py --format table
```

### Step 2: Present matching memories

If one or more memories match, present them to the user as a list with their
topic and summary, and ask which ones to load. For example:

> I found these related memories in the cube:
>
> | File | Topic | Summary |
> | --- | --- | --- |
> | MACHINE_LEARNING-ATTENTION_MECHANISM.md | Attention Mechanism | How scaled dot-product and multi-head attention work |
>
> Would you like me to load any of these?

If no memories match, proceed to answer the question normally and optionally
offer to save the answer for future recall.

### Step 3: Load selected memories

Read the files the user selected:

```bash
cat ~/.memory_cube/memory/SELECTED_FILE.md
```

Use the loaded content as context to answer the user's question. You may
supplement with additional information if the memory does not fully cover
the query, but prefer the stored content as the baseline.

## Workflow: Save

### Step 1: Determine what to save

Identify the content the user wants to persist:

- **Conversation excerpt**: The user points to a specific explanation, decision,
  or discussion from the current conversation. Synthesize it into a clean,
  self-contained Markdown document. Do not copy raw conversation turns — distill
  the information into a well-structured document with headings and sections.
- **Generic data**: The user provides or references raw data, notes, or text
  they want stored as-is. Format it as Markdown where reasonable.
- **Update to an existing memory**: The user wants to append new information or
  patch an existing file in the cube.

If the request is ambiguous, ask the user to clarify what content they want
saved.

### Step 2: Choose the filename

1. If the user specifies a topic or filename, use it (normalizing to the naming
   convention in [NAMING_AND_FORMAT.md](references/NAMING_AND_FORMAT.md)).
2. Otherwise, infer a `CATEGORY-SUBTOPIC.md` name from the content.
3. Check whether a file with that name already exists in the target bank:

```bash
python3 scripts/memory-content.py --search "<keyword>" --format json
```

If a file with the same or very similar name exists, decide whether to overwrite,
append, or use a more specific name. Prefer appending when the new content
extends the existing topic.

### Step 3: Write the memory

**New memory (write via stdin):**

```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin -o "CATEGORY-SUBTOPIC.md" --bank memory
```

**Append to existing memory:**

```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin --append -o "CATEGORY-SUBTOPIC.md" --bank memory
```

**Apply a diff to an existing memory:**

```bash
echo "${DIFF}" | python3 scripts/memorize.py --diff --stdin -o "CATEGORY-SUBTOPIC.md" --bank memory
```

**Copy from a file:**

```bash
python3 scripts/memorize.py -i /path/to/source.md -o "CATEGORY-SUBTOPIC.md" --bank memory
```

### Step 4: Confirm to the user

After a successful write, report:
- The filename and full path of the saved memory.
- A one-line summary of what was saved.
- Whether the file was created, overwritten, or appended to.

## Workflow: Personality Save

This workflow is triggered **proactively** when the user expresses a preference
about agent behavior, tone, mood, specialization, or workflow rules — unlike
the memory save workflow which requires an explicit user request.

### Step 1: Detect and confirm

When the user says something that implies a behavioral change (see the trigger
examples under "Bank Selection Rules" above), acknowledge the preference and
ask whether to persist it:

> Got it — I'll [description of the change]. Would you like me to save this to
> the personality bank so it applies in future conversations?

If the user declines, apply the preference for the current session only. If
they confirm, proceed to Step 2.

### Step 2: Choose the filename

1. Determine the personality category (`TONE`, `MOOD`, `SPECIALIZATION`,
   `RULES`, `SKILLS`, or `PREFERENCES`) from the nature of the request.
2. Generate a `CATEGORY-SUBTOPIC.md` filename following the naming convention
   in [NAMING_AND_FORMAT.md](references/NAMING_AND_FORMAT.md).
3. Check for existing personality entries that overlap:

```bash
python3 scripts/memory-content.py --bank personality --search "<keyword>" --format json
```

If a related entry exists, decide whether to overwrite (the preference
replaces the old one), append (the preference extends it), or create a new
file (the preferences are distinct).

### Step 3: Write the personality entry

Format the content as a short, actionable personality file with frontmatter
(see the Personality Bank Files section in NAMING_AND_FORMAT.md).

```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin -o "CATEGORY-SUBTOPIC.md" --bank personality
```

To update an existing entry:

```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin --append -o "CATEGORY-SUBTOPIC.md" --bank personality
```

### Step 4: Confirm to the user

Report what was saved, the filename, and whether it was created or updated.

## Workflow: Personality Recall

At the start of a conversation (or when context suggests it), load relevant
personality entries to configure agent behavior.

### Step 1: Scan the personality bank

```bash
python3 scripts/memory-content.py --bank personality --format json
```

### Step 2: Load and apply

Read each personality file and apply the preferences silently — do not narrate
every loaded preference to the user unless they ask. Personality entries take
effect as behavioral constraints for the conversation.

```bash
cat ~/.memory_cube/personality/SELECTED_FILE.md
```

If multiple entries conflict (e.g., one says "be concise" and another says "be
detailed"), prefer the most recently saved entry. If the conflict is ambiguous,
ask the user which preference to follow.

### Step 3: Handle missing or empty bank

If the personality bank is empty or does not exist, proceed with default agent
behavior — no special action needed.

## Workflow: Personality Update

When the user changes a preference that already has an entry in the personality
bank, update the existing file rather than creating a duplicate.

### Step 1: Identify the existing entry

```bash
python3 scripts/memory-content.py --bank personality --search "<keyword>" --format json
```

### Step 2: Decide the update strategy

- **Replace**: The new preference supersedes the old one entirely (e.g., "be
  formal" replacing "be casual"). Overwrite the file.
- **Amend**: The new preference adds a nuance to the existing one (e.g., "also
  avoid jargon" added to an existing tone preference). Append or apply a diff.
- **Remove**: The user explicitly revokes a preference (e.g., "stop being
  formal, go back to default"). Delete the file.

### Step 3: Execute

**Overwrite:**
```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin -o "CATEGORY-SUBTOPIC.md" --bank personality
```

**Append:**
```bash
echo "${CONTENT}" | python3 scripts/memorize.py --stdin --append -o "CATEGORY-SUBTOPIC.md" --bank personality
```

**Delete:**
```bash
rm ~/.memory_cube/personality/CATEGORY-SUBTOPIC.md
```

### Step 4: Confirm

Report what changed and how the agent's behavior will adjust.

## Error Handling, Gotchas, and Security

Read [the reference guide](references/REFERENCE.md) for the full error handling
table, common gotchas (heredocs, append separators, case sensitivity, diff
format), and security considerations (no secrets, no path traversal, filesystem
permissions).
