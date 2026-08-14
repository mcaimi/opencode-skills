# Git History Summarizer — Reference

Technical reference for the git-summary skill. For output templates and schemas, see [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md).

## Git commands reference

```bash
# Commit history with stats (with optional limit)
git log --stat --format='%H|%h|%an|%ae|%aI|%s|%b' [-n MAX_COMMITS] [BRANCH]

# Detailed file changes for a single commit
git show --stat --format='%H|%h|%an|%ae|%aI|%s|%b' COMMIT_HASH

# Commit count
git rev-list --count [--max-count=MAX_COMMITS] [BRANCH]

# Unique authors
git log --format='%an|%ae' | sort -u

# File modification frequency
git log --name-only --format='' | sort | uniq -c | sort -rn
```
