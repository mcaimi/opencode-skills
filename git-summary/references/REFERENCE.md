# Git History Summarizer — Reference

Technical reference for the git-summary skill. For output templates and schemas, see [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md).

## Git commands reference

### Core commit data

```bash
# Commit history with stats (with optional limit)
git log --stat --format='%H|%h|%an|%ae|%aI|%s|%b' [-n MAX_COMMITS] [BRANCH]

# Detailed file changes for a single commit
git show --stat --format='%H|%h|%an|%ae|%aI|%s|%b' COMMIT_HASH

# Machine-parseable per-file add/delete counts (preferred over --stat for aggregation)
git log --numstat --format='%H|%h|%an|%ae|%aI|%s' [-n MAX_COMMITS] [BRANCH]

# Commit count
git rev-list --count [--max-count=MAX_COMMITS] [BRANCH]

# Unique authors
git log --format='%an|%ae' | sort -u

# Author ranking by commit count (more efficient than manual aggregation)
git shortlog -sn [--no-merges] [BRANCH]
```

### File modification analysis

```bash
# File modification frequency
git log --name-only --format='' | sort | uniq -c | sort -rn

# File lifecycle — newly added files
git log --diff-filter=A --name-only --format='' [--since=DATE]

# File lifecycle — deleted files
git log --diff-filter=D --name-only --format='' [--since=DATE]

# File lifecycle — renamed files (shows old -> new path)
git log --diff-filter=R --name-status --format=''

# Track a single file across renames
git log --follow --format='%H|%h|%an|%aI|%s' -- FILE_PATH

# Filter commits by change type: A=added, D=deleted, M=modified, R=renamed, C=copied
git log --diff-filter=ADMRC --name-status --format='%H|%aI|%s'
```

### Code churn and hotspot detection

```bash
# Per-file churn (additions + deletions) for hotspot analysis
# High churn files = frequently rewritten, potential instability
git log --numstat --format='' | awk '{add[$3]+=$1; del[$3]+=$2} END {for(f in add) print add[f]+del[f], add[f], del[f], f}' | sort -rn

# Churn within a date range
git log --numstat --format='' --since=DATE --until=DATE | awk '{add[$3]+=$1; del[$3]+=$2} END {for(f in add) print add[f]+del[f], add[f], del[f], f}' | sort -rn

# Binary files in changes (numstat shows '-' for binary)
git log --numstat --format='' | grep '^-' | awk '{print $3}' | sort -u
```

### Branch and merge topology

```bash
# Merge commits only
git log --merges --format='%H|%h|%an|%aI|%s' [-n MAX_COMMITS]

# Non-merge commits only (actual development work)
git log --no-merges --format='%H|%h|%an|%aI|%s' [-n MAX_COMMITS]

# Mainline history (first-parent only, skips merged branch detail)
git log --first-parent --format='%H|%h|%an|%aI|%s' [-n MAX_COMMITS]

# Branches merged into a target branch
git branch -r --merged [BRANCH]

# Branches not yet merged into a target branch
git branch -r --no-merged [BRANCH]

# Parent count per commit (>1 = merge commit)
git log --format='%H %P' | awk '{print NF-1, $1}'
```

### Tag and release analysis

```bash
# List tags with creation dates (sorted newest first)
git tag --sort=-creatordate --format='%(refname:short)|%(creatordate:iso)'

# Commits between two tags/releases
git log --oneline TAG1..TAG2

# Commit count between two tags (release size)
git rev-list --count TAG1..TAG2

# Most recent tag reachable from HEAD
git describe --tags --abbrev=0

# Tags with their annotated messages
git tag -l --format='%(refname:short)|%(creatordate:iso)|%(subject)'
```

### Code ownership and collaboration

```bash
# Authors per file (who has worked on this file)
git log --format='%an' -- FILE_PATH | sort | uniq -c | sort -rn

# Files per author (what has this person worked on)
git log --author=AUTHOR --name-only --format='' | sort | uniq -c | sort -rn

# Distinguish author from committer (e.g. for rebased/cherry-picked work)
git log --format='%an|%ae|%cn|%ce|%H'

# Co-authored commits (from commit trailers)
git log --format='%H|%b' | grep -B1 'Co-authored-by:'
```

### Temporal patterns

```bash
# Daily commit frequency
git log --format='%aI' | cut -dT -f1 | uniq -c | sort -k2

# Hourly distribution (activity heatmap data)
git log --format='%aI' | cut -dT -f2 | cut -d: -f1 | sort | uniq -c

# Day-of-week distribution
git log --format='%ad' --date=format:'%A' | sort | uniq -c | sort -rn

# Weekly commit counts
git log --format='%aI' | cut -dT -f1 | xargs -I{} date -j -f '%Y-%m-%d' '{}' '+%Y-W%V' 2>/dev/null | uniq -c

# Commits per month
git log --format='%ad' --date=format:'%Y-%m' | uniq -c
```

### Commit message analysis

```bash
# Subjects only (for convention/pattern analysis)
git log --format='%s' [-n MAX_COMMITS]

# Detect conventional commit prefixes (feat, fix, chore, etc.)
git log --format='%s' | grep -oE '^[a-z]+(\([^)]*\))?:' | sort | uniq -c | sort -rn

# Average subject length
git log --format='%s' | awk '{total+=length; count++} END {print total/count}'

# Commits referencing issues (e.g. #123, JIRA-456)
git log --format='%H|%s' | grep -E '#[0-9]+|[A-Z]+-[0-9]+'
```

### Repository health

```bash
# Detect shallow clone
git rev-parse --is-shallow-repository

# Repository size (objects)
git count-objects -vH

# Largest files in history (potential bloat)
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print $3, $4}' | sort -rn | head -20

# Stale branches (branches with no commits in the last N days)
git for-each-ref --sort=committerdate --format='%(committerdate:iso)|%(refname:short)' refs/heads/
```
