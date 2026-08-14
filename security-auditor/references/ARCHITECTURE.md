# Security Auditor - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Security Auditor Skill v1.2.0                      │
│                           (SKILL.md)                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Orchestrates
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌──────────────────┐    ┌──────────────────┐
│  Git History  │      │ Dependency       │    │ Security         │
│  Analysis     │      │ Discovery        │    │ Scanning         │
│               │      │                  │    │                  │
│ • Commits     │      │ • Python         │    │ • Credential     │
│ • Authors     │      │ • JavaScript     │    │   Detection      │
│ • Activity    │      │ • Java/Maven     │    │ • Config Audit   │
│ • Patterns    │      │ • Java/Gradle    │    │ • Container      │
│               │      │ • Ruby           │    │   Security       │
│               │      │ • Go             │    │                  │
│               │      │ • .NET           │    │                  │
│               │      │ • Rust           │    │                  │
│               │      │ • PHP            │    │                  │
│               │      │ • Docker         │    │                  │
└───────────────┘      └──────────────────┘    └─────────┬────────┘
                                                          │
                                                          │
                              ┌───────────────────────────┼──────────────────────────┐
                              │                           │                          │
                              ▼                           ▼                          ▼
                    ┌──────────────────┐        ┌──────────────────┐     ┌──────────────────┐
                    │ Pattern-Based    │        │ Entropy-Based    │     │ Permission-Based │
                    │ Detection        │        │ Detection        │     │ Analysis         │
                    │                  │        │                  │     │                  │
                    │ • AWS Keys       │        │ • Shannon        │     │ • File perms     │
                    │ • Google Keys    │        │   Entropy        │     │ • SUID/SGID      │
                    │ • GitHub Tokens  │        │ • High-entropy   │     │ • World-readable │
                    │ • Slack Tokens   │        │   strings        │     │ • Writable       │
                    │ • Private Keys   │        │ • Confidence     │     │   configs        │
                    │ • JWT Tokens     │        │   scoring        │     │                  │
                    │ • DB Credentials │        │ • False positive │     │                  │
                    │ • Generic        │        │   filtering      │     │                  │
                    │   patterns       │        │                  │     │                  │
                    └──────────────────┘        └────────┬─────────┘     └──────────────────┘
                                                         │
                                                         │ Uses
                                                         │
                                                         ▼
                                              ┌──────────────────────┐
                                              │ entropy_detector.py  │
                                              │                      │
                                              │ • Standalone tool    │
                                              │ • CLI interface      │
                                              │ • JSON/CSV output    │
                                              │ • Configurable       │
                                              └──────────────────────┘
```

## Data Flow

```
┌─────────────┐
│  User Input │
│             │
│ • Repo path │
│ • Branch    │
│ • Remediate │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 1: Repository Validation           │
│  • Check git repo                        │
│  • Validate paths                        │
│  • Check permissions                     │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 2: Git History Extraction          │
│  • Extract commits                       │
│  • Parse authors                         │
│  • Analyze patterns                      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 3: Dependency Discovery            │
│  • Auto-detect project type(s)           │
│  • Run language-specific commands        │
│  • Parse dependency manifests            │
│  • Extract versions                      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 4: Security Analysis               │
│  ┌────────────────────────────────────┐  │
│  │ a. Credential Detection            │  │
│  │    • Pattern matching              │  │
│  │    • Entropy analysis              │  │
│  │    • Confidence scoring            │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ b. Code Security                   │  │
│  │    • Injection vulnerabilities     │  │
│  │    • Crypto issues                 │  │
│  │    • CWE/OWASP mapping             │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ c. Configuration Security          │  │
│  │    • File permissions              │  │
│  │    • Unencrypted keys              │  │
│  │    • .gitignore validation         │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ d. Container Security              │  │
│  │    • Dockerfile analysis           │  │
│  │    • docker-compose security       │  │
│  │    • Best practices                │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ e. Dependency Vulnerabilities      │  │
│  │    • CVE lookup                    │  │
│  │    • CVSS scoring                  │  │
│  │    • Fix availability              │  │
│  └────────────────────────────────────┘  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 5: Scoring & Compliance            │
│  • Calculate security score (0-100)      │
│  • Assign letter grade (A-F)             │
│  • Map to OWASP Top 10                   │
│  • Map to CWE Top 25                     │
│  • Map to SANS Top 25                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 6: Report Generation               │
│  • Executive summary                     │
│  • Risk matrix                           │
│  • Detailed findings tables              │
│  • Prioritized remediation plan          │
│  • Compliance status                     │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  Step 7: Output                          │
│                                          │
│  ┌────────────┐    ┌─────────────────┐  │
│  │ Markdown   │    │ Optional Auto   │  │
│  │ Report     │    │ Remediation     │  │
│  │            │    │ (if enabled)    │  │
│  └────────────┘    └─────────────────┘  │
└──────────────────────────────────────────┘
```

## Component Interaction

```
┌──────────────────────────────────────────────────────────────────┐
│                        Main Skill                                │
│                         (SKILL.md)                               │
└───┬──────────────────────────────────────────────────────────┬───┘
    │                                                          │
    │ Executes                                                 │ Uses
    │                                                          │
    ▼                                                          ▼
┌────────────────────────────┐                    ┌──────────────────────┐
│  Shell Commands            │                    │  External Tools      │
│                            │                    │  (optional)          │
│  • grep (pattern search)   │                    │                      │
│  • find (file discovery)   │                    │  • Trivy (Docker)    │
│  • git (history)           │                    │  • pip-audit         │
│  • python3 (entropy)       │                    │  • npm audit         │
│                            │                    │  • bandit            │
└────────────────────────────┘                    │  • semgrep           │
                                                  └──────────────────────┘
┌────────────────────────────┐
│  Standalone Tools          │
│                            │
│  entropy_detector.py       │◄─── Can run independently
│  security_scan.sh          │◄─── Can run independently
│                            │
└────────────────────────────┘

┌────────────────────────────┐
│  Documentation             │
│                            │
│  • references/             │
│    DETAILED_SPEC.md        │
│  • references/             │
│    OUTPUT_FORMAT.md        │
│  • references/             │
│    ARCHITECTURE.md         │
└────────────────────────────┘
```

## Scoring Algorithm

```
Security Score Calculation
─────────────────────────────

Base Score: 100

Deductions:
  Critical Issues:  -40 points each
  High Severity:    -20 points each
  Medium Severity:  -10 points each
  Low Severity:     -5 points each

Final Score = max(0, 100 - total_deductions)

Grading Scale:
  A (90-100): Excellent security posture
  B (80-89):  Good security posture
  C (70-79):  Fair, improvements needed
  D (60-69):  Poor, significant issues
  F (<60):    Critical, immediate action required

Example:
  2 Critical + 3 High + 5 Medium + 4 Low
  = (2×40) + (3×20) + (5×10) + (4×5)
  = 80 + 60 + 50 + 20
  = 210 deductions
  = max(0, 100 - 210)
  = 0 points (Grade F)
```

## Confidence Scoring for Secrets

```
Entropy-Based Confidence
────────────────────────

Base Confidence (from entropy):
  Entropy >= 5.5  → High
  Entropy >= 5.0  → Medium
  Entropy < 5.0   → Low

Context Boost:
  If line contains keywords (password, secret, token, key, api, auth):
    Low → Medium
    Medium → High

Pattern Match Boost:
  If matches known pattern (AWS key, GitHub token, etc.):
    Always → High

Final Confidence:
  High:   Pattern match + high entropy + context
          OR known pattern match
  Medium: High entropy + context
          OR pattern match
  Low:    High entropy only
```

## Tool Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                    Integration Points                   │
└─────────────────────────────────────────────────────────┘

1. CI/CD Integration
   ├─ GitHub Actions
   │  └─ Use security_scan.sh or entropy_detector.py
   │     Exit codes: 0=pass, 1=high issues, 2=critical
   │
   ├─ GitLab CI
   │  └─ Same as GitHub Actions
   │
   └─ Jenkins
      └─ Execute as shell step

2. Pre-commit Hooks
   ├─ Quick secret scan before commit
   │  └─ python3 scripts/entropy_detector.py --min-entropy 5.0
   │
   └─ Configuration validation
      └─ Check file permissions before commit

3. Manual Execution
   ├─ Full scan: bash scripts/security_scan.sh . --full
   ├─ Quick scan: bash scripts/security_scan.sh . --quick
   └─ Entropy only: python3 scripts/entropy_detector.py

4. Scheduled Scans
   └─ Cron job for periodic security audits
      └─ 0 2 * * 0 cd /path/to/repo && bash scripts/security_scan.sh . --full > report.txt
```

## File Structure

```
security-auditor/              # agentskills-format skill
│
├─ SKILL.md                    # Required: metadata + instructions
│
├─ scripts/
│  ├─ entropy_detector.py      # Entropy-based secret detector
│  ├─ security_scan.sh         # Comprehensive security scanner
│  └─ README.md                # Scripts documentation
│
├─ references/
│  ├─ DETAILED_SPEC.md         # Full detection commands reference
│  ├─ OUTPUT_FORMAT.md         # Report template
│  ├─ ARCHITECTURE.md          # This file
│  ├─ QUICKREF.md              # Quick reference guide
│  └─ USAGE_GUIDE.md           # Complete usage guide
│
└─ assets/                     # Static resources
```

## Extension Points

Future enhancements can be added at these points:

1. **New Detection Patterns**
   - Add to pattern list in references/DETAILED_SPEC.md
   - Update scripts/security_scan.sh
   - Update entropy_detector.py if needed

2. **New Project Types**
   - Add dependency discovery commands
   - Update language-specific sections

3. **Integration with External Tools**
   - Add optional tool checks (trivy, bandit, semgrep)
   - Graceful fallback if tool not available

4. **Custom Reporting**
   - Add new output format generators
   - Support JSON/HTML/PDF output

5. **Automated Remediation**
   - Implement fix strategies per issue type
   - Generate fix commits

## Performance Characteristics

```
Typical Performance (on medium-sized repo ~1000 files):

Pattern-based secret detection:   1-3 seconds
Entropy analysis:                  5-15 seconds
Configuration scanning:            1-2 seconds
Docker analysis:                   <1 second
Full scan:                         10-25 seconds

Memory usage:                      <50 MB
CPU usage:                         1 core (single-threaded)

Optimization opportunities:
  • Parallel grep operations
  • Incremental scanning (only changed files)
  • Result caching
```

## Security Considerations

```
The agent itself follows security best practices:

1. Read-only by default
   - No destructive operations unless remediate=true
   - Ask permission before write operations

2. No credential exposure
   - Secrets are masked in output
   - Never sends credentials to external services

3. Sandboxed execution
   - Uses standard Unix tools
   - No arbitrary code execution from repo

4. Privacy-preserving
   - All scanning is local
   - Optional: CVE lookups use public APIs only
```

## Summary

The Security Auditor Agent architecture is designed to be:

- **Modular**: Independent components that can be used standalone
- **Extensible**: Easy to add new detection patterns and tools
- **Production-ready**: Suitable for CI/CD integration
- **Comprehensive**: Multi-layer security analysis
- **Actionable**: Clear scoring and prioritized remediation

The implementation balances thoroughness with performance, providing detailed security insights while maintaining reasonable execution times.
