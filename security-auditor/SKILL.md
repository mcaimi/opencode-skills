---
name: security-auditor
description: >-
  Analyze codebases for security vulnerabilities: credential leaks (AWS keys,
  GitHub tokens, API keys, private keys, JWT tokens, database credentials),
  configuration security issues (file permissions, unencrypted keys, missing
  gitignore entries), container and Docker security (Dockerfile best practices,
  docker-compose hardening), dependency CVEs across Python, JavaScript, Java,
  Go, Ruby, Rust, PHP, and .NET, and code security bugs (injection, XSS,
  insecure crypto). Generates comprehensive Markdown reports with A-F severity
  scoring, OWASP Top 10 / CWE Top 25 / SANS Top 25 compliance mapping, and
  prioritized remediation plans. Use when asked to audit a repository, check
  for leaked secrets, review Docker security, scan dependencies for
  vulnerabilities, run a security scan, or assess overall security posture.
compatibility: >-
  Requires bash, python3, and git. Optional tools for deeper analysis: trivy,
  bandit, semgrep, pip-audit, npm audit, govulncheck, cargo audit.
metadata:
  author: mcaimi
  version: "1.2.0"
allowed-tools: Bash Read Write Edit WebFetch WebSearch
---

# Security Auditor

Analyze a codebase for security issues, generate a detailed report, and
optionally remediate findings.

## Input Parameters

### Required

- `repository_path` (string): Absolute path to the code repository.

### Optional

- `branch` (string): Branch to analyze (default: current branch).
- `remediate` (bool): When false, generate a report only. When true, also edit
  code to fix issues (default: false).

## Available Scripts

- **`scripts/security_scan.sh`** — Comprehensive security scanner covering
  secrets, configuration, and container security. Supports `--full`, `--quick`,
  `--secrets-only`, `--config-only`, `--docker-only` modes.
- **`scripts/entropy_detector.py`** — Shannon entropy-based secret detector.
  Supports `--min-entropy`, `--min-length`, and `--format` (text/json/csv).

## Workflow

### Step 1: Validate Repository

```bash
cd "$REPOSITORY_PATH"
git rev-parse --is-inside-work-tree 2>/dev/null || echo "not-a-git-repo"
git rev-parse --abbrev-ref HEAD 2>/dev/null
```

Check that the path exists, is readable, and resolve the absolute path.

### Step 2: Extract Git History

```bash
git log --stat --format='%H|%h|%an|%ae|%aI|%s|%b' [-n MAX_COMMITS] [BRANCH]
git rev-list --count [BRANCH]
git log --format='%an|%ae' | sort -u
git log --name-only --format='' | sort | uniq -c | sort -rn
```

Parse commits, authors, dates, and file change statistics. Look for suspicious
patterns: unusually large commits, activity at unusual times, modifications to
sensitive files (auth, crypto, permissions) by unfamiliar contributors.

### Step 3: Discover Dependencies

Auto-detect project types by searching for dependency manifests, then extract
package names and versions. Read `references/DETAILED_SPEC.md` for the
complete set of discovery commands per language ecosystem (Python, JavaScript,
Java/Maven, Java/Gradle, Ruby, Go, .NET, Rust, PHP, Docker).

### Step 4: Security Analysis

Run all applicable analysis categories:

**a. Credential & Secret Detection**

Combine pattern-based detection with entropy analysis for comprehensive
coverage. Run the pattern-based grep commands first, then the entropy detector:

```bash
bash scripts/security_scan.sh "$REPOSITORY_PATH" --secrets-only
python3 scripts/entropy_detector.py "$REPOSITORY_PATH" --format json
```

Read `references/DETAILED_SPEC.md` for the full set of detection patterns
(AWS keys, Google API keys, GitHub tokens, Slack tokens, private keys, JWT
tokens, database credentials, generic secret patterns).

Assign confidence levels:
- **High**: Pattern match + high entropy + sensitive context keyword
- **Medium**: Pattern match OR high entropy with context
- **Low**: High entropy only

**b. Code Security Analysis**

Scan for injection vulnerabilities (SQL, command, XSS), insecure cryptography,
authentication/authorization flaws, path traversal, insecure deserialization,
and missing input validation. Map each finding to its CWE identifier and
OWASP Top 10 category.

**c. Configuration Security**

```bash
bash scripts/security_scan.sh "$REPOSITORY_PATH" --config-only
```

Check file permissions on sensitive files, find unencrypted private keys,
validate .gitignore completeness, detect SUID/SGID bits. Report current vs.
recommended permissions for each finding.

**d. Container Security**

```bash
bash scripts/security_scan.sh "$REPOSITORY_PATH" --docker-only
```

Analyze Dockerfiles for base image issues, root user, hardcoded secrets,
missing HEALTHCHECK, ADD vs COPY, exposed risky ports. Check docker-compose
for privileged mode, host networking, and sensitive volume mounts. Run Trivy
if available.

**e. Dependency Vulnerabilities**

For each dependency found in Step 3, query for known CVEs using WebSearch:
`"{package_name} {version} CVE vulnerability"`. Cross-reference with the
National Vulnerability Database. Prioritize by CVSS score and note fix
availability.

If WebFetch or WebSearch fails, omit this section from the report rather than
failing the entire audit.

### Step 5: Calculate Security Score

```
Base Score: 100
  Critical: -40 points each
  High:     -20 points each
  Medium:   -10 points each
  Low:      -5 points each

Final Score = max(0, 100 - deductions)

Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)
```

### Step 6: Map to Security Standards

Map each finding to applicable standards:
- OWASP Top 10 (2021): A01 through A10
- CWE Top 25 Most Dangerous Software Weaknesses
- SANS Top 25 Most Dangerous Programming Errors

Report compliance status (Pass/Fail) for each standard.

### Step 7: Generate Report

Produce the report in Markdown using the template in
`references/OUTPUT_FORMAT.md`. The report must include:
- Executive summary with security score and grade
- Risk matrix with severity counts and estimated remediation time
- Security standards compliance table
- Repository statistics (commits, authors, date range)
- Detailed findings tables per category (credentials, config, container, code,
  dependencies), each with file path, line number, and severity
- Prioritized remediation plan (immediate/short-term/long-term)
- Methodology and false positive rate estimate

### Step 8: Optional Remediation

When `remediate` is true:
1. Fix auto-fixable issues (dependency updates, permission corrections,
   gitignore additions, Dockerfile improvements).
2. Create descriptive commit messages for each fix.
3. Present issues requiring manual review separately.
4. Still generate the full report even when auto-remediating.

## Gotchas

- The `find` command's `--exclude-dir` brace expansion syntax
  (`--exclude-dir={.git,node_modules}`) is a bash extension. It works in grep
  but not in find. For find, use multiple `-not -path` clauses.
- Always exclude `.git`, `node_modules`, `vendor`, `venv`, `.venv`, `build`,
  `dist`, and `target` directories from all scans.
- Skip `.min.js`, `.map`, `.lock`, `.log`, and `.svg` files to reduce false
  positives in secret detection.
- `.env.example` and `.env.template` are NOT secrets — exclude them from
  credential findings.
- Strings longer than 200 characters with high entropy are usually serialized
  data, not secrets.
- Git commit hashes (40 hex chars), MD5 hashes, version numbers, and URLs
  trigger false positives in entropy detection — filter them out.
- A repository may contain multiple project types simultaneously (e.g., Python
  backend + JavaScript frontend). Run dependency discovery for all detected
  types.
- When running `find`, search from `.` or a specific path, never from `/`.
- Exit codes from `scripts/security_scan.sh`: 0 = no critical/high issues,
  1 = high severity found, 2 = critical severity found.
- WebFetch/WebSearch failures for CVE lookups are non-critical. Omit the
  dependency vulnerability section rather than failing the audit.

## Error Handling

- **Invalid path**: Report that the path does not exist or is not readable.
- **Not a git repo**: Proceed with security scanning but skip git history
  analysis. Note this in the report.
- **No commits**: Report empty repository with appropriate message.
- **Git command failure**: Report the error with command output.
- **Web fetch failure**: Non-critical — omit CVE data from report.

## Security Considerations

- **Path validation**: Validate repository paths to prevent directory traversal.
- **Execution limits**: Enforce timeout limits to prevent resource exhaustion.
- **Credential handling**: Never expose discovered credentials in full — mask
  the middle portion in report output.
- **Read-only default**: Do not modify any files unless `remediate` is true.
