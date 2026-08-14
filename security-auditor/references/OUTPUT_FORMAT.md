# Security Audit Report Template

Use this template when generating the final Markdown report. Adapt sections
based on actual findings — omit empty sections but keep the overall structure.

```markdown
# Security Audit Report

**Repository:** {repository_path}
**Branch:** {branch_name}
**Analysis Date:** {timestamp}
**Report Version:** 1.2.0

---

## Executive Summary

### Overall Security Score: {A-F Grade}

**Score Calculation:**
- Critical Issues: {count} (-40 points each)
- High Severity: {count} (-20 points each)
- Medium Severity: {count} (-10 points each)
- Low Severity: {count} (-5 points each)
- Base Score: 100

**Security Posture:** {Excellent/Good/Fair/Poor/Critical}

### Key Findings
- **Critical:** {count} issues requiring immediate attention
- **High:** {count} issues requiring prompt remediation
- **Medium:** {count} issues to address in near term
- **Low:** {count} issues for long-term improvement

### Risk Summary
- **Credential Leaks Detected:** {yes/no} ({count} instances)
- **Vulnerable Dependencies:** {count} packages with known CVEs
- **Configuration Issues:** {count} insecure configurations found
- **Container Security Issues:** {count} Docker-related issues
- **Code Security Issues:** {count} vulnerable code patterns

---

## Risk Matrix

| Risk Level | Count | Top Issue Types | Estimated Remediation Time |
|------------|-------|-----------------|----------------------------|
| Critical   | {n}   | {top 3 types}   | {hours} hours              |
| High       | {n}   | {top 3 types}   | {hours} hours              |
| Medium     | {n}   | {top 3 types}   | {days} days                |
| Low        | {n}   | {top 3 types}   | {days} days                |

### Security Standards Compliance

| Standard | Issues Found | Status |
|----------|--------------|--------|
| OWASP Top 10 2021 | {count} violations | {Pass/Fail} |
| CWE Top 25 | {count} violations | {Pass/Fail} |
| SANS Top 25 | {count} violations | {Pass/Fail} |

---

## Repository Statistics

- **Total Commits:** {count}
- **Authors:** {author_count}
- **Date Range:** {first_commit_date} to {last_commit_date}
- **Files Modified:** {file_count}
- **Lines Added:** {additions}
- **Lines Deleted:** {deletions}

### Top Contributors

| Author | Commits | Lines Added | Lines Deleted |
|--------|---------|-------------|---------------|
| ...    | ...     | ...         | ...           |

### Most Modified Files

| File Path | Commits | Total Changes |
|-----------|---------|---------------|
| ...       | ...     | ...           |

### Development Patterns

- **Peak Activity Day:** {day_of_week}
- **Peak Activity Hour:** {hour}
- **Average Commit Size:** {avg_changes} lines
- **Merge Commits:** {merge_count}
- **Suspicious Activity Detected:** {yes/no}

---

## Credential Leaks & Secrets

### Summary
- **Total Secrets Found:** {count}
- **High-Entropy Strings:** {count}
- **Pattern Matches:** {count}
- **Files Affected:** {count}

| Issue ID | Severity | File Path | Line | Secret Type | Pattern/Entropy | Confidence |
|----------|----------|-----------|------|-------------|-----------------|------------|
| ...      | ...      | ...       | ...  | ...         | ...             | ...        |

**Secret Types Detected:**
- API Keys (AWS, GCP, Azure, GitHub, etc.)
- Passwords and Credentials
- Private Keys and Certificates
- OAuth Tokens and JWT Secrets
- Database Connection Strings
- High-Entropy Strings (potential secrets)

---

## Configuration Security Issues

### Summary
- **Insecure File Permissions:** {count}
- **Exposed Sensitive Files:** {count}
- **Missing .gitignore Entries:** {count}

| Issue ID | Severity | File Path | Issue Type | Current Perms | Recommended Perms |
|----------|----------|-----------|------------|---------------|-------------------|
| ...      | ...      | ...       | ...        | ...           | ...               |

---

## Container Security Issues

### Summary
- **Dockerfiles Analyzed:** {count}
- **Base Image Issues:** {count}
- **Configuration Issues:** {count}
- **Best Practice Violations:** {count}

| Issue ID | Severity | Dockerfile | Line | Issue Description | Recommendation |
|----------|----------|------------|------|-------------------|----------------|
| ...      | ...      | ...        | ...  | ...               | ...            |

---

## Code Security Issues

| Issue ID | Severity | CWE | File Path | Line | Issue Type | Code Snippet | OWASP Category |
|----------|----------|-----|-----------|------|------------|--------------|----------------|
| ...      | ...      | ... | ...       | ...  | ...        | ...          | ...            |

---

## Dependency Vulnerabilities

### Summary
- **Total Dependencies:** {count}
- **Vulnerable Dependencies:** {count}
- **Total CVEs:** {count}
- **Projects Analyzed:** {list of project types}

| Dependency Name | Version | Severity | CVE ID | CVSS Score | Description | Fix Available |
|-----------------|---------|----------|--------|------------|-------------|---------------|
| ...             | ...     | ...      | ...    | ...        | ...         | ...           |

---

## Remediation Plan

### Immediate Actions (Critical/High Priority)

| Issue ID | Severity | Category | File Path | Remediation Action | Estimated Time |
|----------|----------|----------|-----------|-------------------|----------------|
| ...      | Critical | ...      | ...       | ...               | ...            |

### Short-term Actions (Medium Priority)

| Issue ID | Severity | Category | File Path | Remediation Action | Estimated Time |
|----------|----------|----------|-----------|-------------------|----------------|
| ...      | Medium   | ...      | ...       | ...               | ...            |

### Long-term Improvements (Low Priority)

| Issue ID | Severity | Category | File Path | Remediation Action | Estimated Time |
|----------|----------|----------|-----------|-------------------|----------------|
| ...      | Low      | ...      | ...       | ...               | ...            |

### Automated Fixes Available

The following issues can be automatically remediated by setting `remediate: true`:
- {list of auto-fixable issues}

### Manual Review Required

The following issues require manual intervention:
- {list of issues requiring human judgment}

---

## Detailed Findings

{Detailed breakdown of each finding with context, affected code, and
remediation guidance}

---

## Appendix

### Tools Used
- Git history analysis
- Enhanced credential detection (pattern matching + entropy analysis)
- Configuration file security scanner
- Container security scanner (Docker)
- Dependency vulnerability scanner

### Methodology
- Pattern-based secret detection
- Shannon entropy analysis for high-entropy strings
- File permission validation
- Dockerfile best practice validation
- CVE database correlation

### False Positive Rate
Estimated false positive rate: {percentage}% based on confidence scores
```
