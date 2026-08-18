# Git History Summarizer — Output Format

Output templates and schemas for the git-summary skill.

## Markdown output template

```markdown
# Git History Summary

**Repository:** {repository_path}
**Branch:** {branch_name}
**Analysis Date:** {timestamp}
**Commits Analyzed:** {commit_count}
**Limit Applied:** {max_commits} (if applicable)

## Summary Statistics

- **Total Commits:** {count}
- **Authors:** {author_count}
- **Date Range:** {first_commit_date} to {last_commit_date}
- **Files Modified:** {file_count}
- **Lines Added:** {additions}
- **Lines Deleted:** {deletions}

## Top Contributors

| Author | Commits | Lines Added | Lines Deleted |
|--------|---------|-------------|---------------|
| ...    | ...     | ...         | ...           |

## Commit Timeline

### {Date or Time Period}

#### Commit: {short_hash} - {commit_message}
- **Author:** {author_name} <{author_email}>
- **Date:** {commit_date}
- **Files Changed:** {file_count}
- **Changes:** +{additions} -{deletions}

**Modified Files:**
- `{file_path}` (+{add} -{del})

**Full Message:**
{full_commit_message}

---

## Most Modified Files

| File Path | Commits | Total Changes |
|-----------|---------|---------------|
| ...       | ...     | ...           |

## Code Churn Hotspots

| File Path | Additions | Deletions | Churn (Add+Del) |
|-----------|-----------|-----------|-----------------|
| ...       | ...       | ...       | ...             |

> High-churn files are frequently rewritten and may indicate instability or active development.

## File Lifecycle

### Files Added
| File Path | Date Added | Author |
|-----------|------------|--------|
| ...       | ...        | ...    |

### Files Deleted
| File Path | Date Deleted | Author |
|-----------|--------------|--------|
| ...       | ...          | ...    |

### Files Renamed
| Old Path | New Path | Date | Author |
|----------|----------|------|--------|
| ...      | ...      | ...  | ...    |

## Tag / Release History

| Tag | Date | Commits Since Previous |
|-----|------|------------------------|
| ... | ...  | ...                    |

## Code Ownership

| File Path | Primary Author | Other Contributors |
|-----------|----------------|--------------------|
| ...       | ...            | ...                |

## Commit Conventions

### Prefix Distribution
| Prefix | Count | Percentage |
|--------|-------|------------|
| feat   | ...   | ...        |
| fix    | ...   | ...        |
| ...    | ...   | ...        |

### Issue References
- **Total commits referencing issues:** {count}
- **Trackers detected:** {tracker_names}

## Development Patterns

- **Peak Activity Day:** {day_of_week}
- **Peak Activity Hour:** {hour}
- **Average Commit Size:** {avg_changes} lines
- **Merge Commits:** {merge_count}
```

## JSON output schema

When the user requests JSON output, use this structure:

```json
{
  "repository": "string",
  "branch": "string",
  "analysis_date": "ISO-8601-timestamp",
  "limits": {
    "max_commits": "number|null",
    "since_date": "string|null",
    "until_date": "string|null"
  },
  "summary": {
    "total_commits": "number",
    "author_count": "number",
    "date_range": {
      "first_commit": "ISO-8601-timestamp",
      "last_commit": "ISO-8601-timestamp"
    },
    "changes": {
      "files_modified": "number",
      "lines_added": "number",
      "lines_deleted": "number"
    }
  },
  "authors": [
    {
      "name": "string",
      "email": "string",
      "commits": "number",
      "lines_added": "number",
      "lines_deleted": "number"
    }
  ],
  "commits": [
    {
      "hash": "string",
      "short_hash": "string",
      "author": {
        "name": "string",
        "email": "string"
      },
      "date": "ISO-8601-timestamp",
      "message": "string",
      "files": [
        {
          "path": "string",
          "additions": "number",
          "deletions": "number",
          "status": "modified|added|deleted|renamed"
        }
      ],
      "stats": {
        "files_changed": "number",
        "additions": "number",
        "deletions": "number"
      }
    }
  ],
  "file_impact": [
    {
      "path": "string",
      "commit_count": "number",
      "total_changes": "number"
    }
  ],
  "code_churn": [
    {
      "path": "string",
      "additions": "number",
      "deletions": "number",
      "churn": "number"
    }
  ],
  "file_lifecycle": {
    "added": [
      {
        "path": "string",
        "date": "ISO-8601-timestamp",
        "author": "string"
      }
    ],
    "deleted": [
      {
        "path": "string",
        "date": "ISO-8601-timestamp",
        "author": "string"
      }
    ],
    "renamed": [
      {
        "old_path": "string",
        "new_path": "string",
        "date": "ISO-8601-timestamp",
        "author": "string"
      }
    ]
  },
  "tags": [
    {
      "name": "string",
      "date": "ISO-8601-timestamp",
      "commits_since_previous": "number|null"
    }
  ],
  "code_ownership": [
    {
      "path": "string",
      "primary_author": "string",
      "contributors": ["string"]
    }
  ],
  "commit_conventions": {
    "prefixes": [
      {
        "prefix": "string",
        "count": "number",
        "percentage": "number"
      }
    ],
    "issue_references": {
      "total": "number",
      "trackers": ["string"]
    }
  },
  "patterns": {
    "peak_activity_day": "string",
    "peak_activity_hour": "number",
    "average_commit_size": "number",
    "merge_commits": "number"
  }
}
```
