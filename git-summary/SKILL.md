---
name: git-summary
description: >-
  Analyzes git repository histories and produces structured summaries of commits,
  changes, and development patterns. Use when the user asks for a git history summary,
  commit analysis, contributor statistics, change patterns, or repository activity reports.
  Supports filtering by author, date range, branch, file path, and commit count.
license: Apache-2.0
compatibility: Requires git
metadata:
  author: mcaimi
  version: "1.0.0"
allowed-tools: Bash(git:*)
---

# Git History Summarizer

Analyze a git repository's commit history and produce a detailed, structured markdown report.

## Instructions

### 1. Determine scope

Gather the following from the user's request (use defaults when not specified):

| Parameter         | Default          | Notes                                      |
|-------------------|------------------|---------------------------------------------|
| Repository path   | Current directory | Must be a valid git repository              |
| Max commits       | Unlimited        | Integer 1-10000; limits to most recent N    |
| Branch            | Current branch   | Verify it exists before proceeding          |
| Author filter     | All authors      | Match by name or email                      |
| Since / until     | No limit         | ISO 8601 dates                              |
| File path filter  | All files        | Commits touching this path only             |
| Include diffs     | No               | Adds per-file +/- stats (slower)            |

### 2. Validate inputs

1. Confirm the path is a git repository (`git rev-parse --is-inside-work-tree`).
2. If a branch is specified, verify it exists (`git branch --list`).
3. If `max_commits` is given, ensure it is in range 1-10000.
4. If dates are given, verify they parse as ISO 8601.

On validation failure, report the error clearly and stop.

### 3. Extract commit data

Run `git log` with the appropriate filters:

```bash
git log --stat --format='%H|%h|%an|%ae|%aI|%s|%b' [-n MAX_COMMITS] [--author=AUTHOR] [--since=DATE] [--until=DATE] [-- FILE_PATH] [BRANCH]
```

Parse each commit's hash, short hash, author name, author email, date, subject, body, and file change stats.

### 4. Aggregate statistics

Compute:

- Total commits analyzed
- Unique author count
- Date range (first to last commit)
- Total files modified, lines added, lines deleted
- Per-author commit counts and line changes
- Per-file modification frequency

### 5. Detect patterns

- **Peak activity day** — day of the week with the most commits
- **Peak activity hour** — hour (0-23) with the most commits
- **Average commit size** — mean lines changed per commit
- **Merge commit count** — commits with more than one parent

### 6. Generate report

Produce a markdown report with these sections in order:

1. **Header** — repository path, branch, analysis date, commit count, any limits applied
2. **Summary Statistics** — totals for commits, authors, date range, files, lines added/deleted
3. **Top Contributors** — table of authors ranked by commit count with line stats
4. **Commit Timeline** — commits grouped by date, each showing hash, message, author, date, files changed, and change counts
5. **Most Modified Files** — table of files ranked by number of commits touching them
6. **Development Patterns** — peak day, peak hour, average commit size, merge count

See [the output format guide](references/OUTPUT_FORMAT.md) for the full markdown template and JSON schema, and [the reference guide](references/REFERENCE.md) for git commands used.

## Error handling

| Condition              | Action                                          |
|------------------------|-------------------------------------------------|
| Not a git repository   | Report error, stop                              |
| Branch not found       | List available branches, stop                   |
| No commits match       | Return empty summary with explanation           |
| Invalid date format    | Report expected format (ISO 8601), stop         |
| Git command failure    | Report the command and its stderr output, stop  |

## Edge cases

- **Very large repositories** (>10,000 commits): recommend the user set `max_commits` to keep analysis time reasonable.
- **Including diffs**: warn the user this increases processing time significantly on large histories.
- **Detached HEAD**: use `HEAD` as the branch name in the report.
- **Shallow clones**: note in the report that history may be incomplete.

## Security

- Never expose git credentials or tokens in the output.
- Validate repository paths to prevent directory traversal.
