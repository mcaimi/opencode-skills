# Security Auditor - Complete Usage Guide

This guide shows all the ways to use the security-auditor skill and its tools.

## What You Have

```
security-auditor/                    # agentskills-format skill
├── SKILL.md                         # Skill metadata + instructions
├── scripts/
│   ├── entropy_detector.py          # Standalone entropy scanner
│   ├── security_scan.sh             # Standalone comprehensive scanner
│   └── README.md                    # Scripts documentation
├── references/
│   ├── DETAILED_SPEC.md             # Full detection commands
│   ├── OUTPUT_FORMAT.md             # Report template
│   ├── ARCHITECTURE.md              # System architecture
│   ├── QUICKREF.md                  # Quick reference guide
│   └── USAGE_GUIDE.md              # This file
└── assets/                          # Static resources
```

## 🚀 Quick Start

### Method 1: Slash Command (Easiest)

**Install the skill:**
```bash
cd security-auditor/skills
./install.sh --symlink
```

**Use it:**
```bash
# In Claude Code, type:
/security-audit
/security-audit --quick
/security-audit --remediate
```

### Method 2: Natural Language (Simplest)

Just ask Claude:
```
"Run a security audit on this repository"
"Check for leaked secrets"
"Scan for security issues"
```

Claude will spawn the agent automatically.

### Method 3: Standalone Tools (Fastest)

**Quick entropy scan:**
```bash
python3 scripts/entropy_detector.py
```

**Full security scan:**
```bash
./scripts/security_scan.sh . --full
```

## 📊 Comparison

| Method | Speed | Detail | Use Case |
|--------|-------|--------|----------|
| Slash Command | Medium | High | Regular use, convenience |
| Natural Language | Medium | High | One-off audits, exploration |
| Standalone Tools | Fast | Medium | CI/CD, quick checks |
| Manual Commands | Fastest | Low | Specific checks only |

## 🎯 Use Cases

### Use Case 1: Pre-Commit Check

**Goal:** Check for secrets before committing

**Solution:**
```bash
# Quick entropy scan
python3 scripts/entropy_detector.py --min-entropy 5.0

# Or quick security scan
./scripts/security_scan.sh . --secrets-only
```

**Exit codes:**
- `0` = Safe to commit
- `1` = Issues found, review needed

### Use Case 2: Weekly Security Audit

**Goal:** Comprehensive weekly security review

**Solution:**
```bash
# In Claude Code
/security-audit

# Or via standalone tool
./scripts/security_scan.sh . --full > weekly-report.md
```

**Schedule it:**
```bash
# Add to crontab (weekly on Sunday at 2 AM)
0 2 * * 0 cd /path/to/repo && ./scripts/security_scan.sh . --full > report-$(date +\%Y\%m\%d).md
```

### Use Case 3: CI/CD Pipeline

**Goal:** Block merges with security issues

**GitHub Actions:**
```yaml
name: Security Audit

on: [pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Entropy Detection
        run: |
          python3 scripts/entropy_detector.py --min-entropy 5.0
          
      - name: Security Scan
        run: |
          chmod +x scripts/security_scan.sh
          ./scripts/security_scan.sh . --full
```

**Exit codes:**
- `0` = Pass, allow merge
- `1` = High issues, block merge
- `2` = Critical issues, block merge

### Use Case 4: Onboarding New Repo

**Goal:** Assess security posture of new codebase

**Solution:**
```bash
# Full analysis with natural language
"Run a complete security audit on ~/new-project"

# Or with skill
cd ~/new-project
/security-audit
```

**Review:**
- Security score (A-F)
- Priority issues
- Remediation plan

### Use Case 5: Security Incident Response

**Goal:** Quick check if credentials leaked

**Solution:**
```bash
# Fast credential scan
grep -rInE "AKIA[0-9A-Z]{16}" . --exclude-dir=.git  # AWS
grep -rInE "gh[pousr]_[0-9a-zA-Z]{36,}" . --exclude-dir=.git  # GitHub

# Or comprehensive
python3 scripts/entropy_detector.py --format json > results.json
```

### Use Case 6: Docker Security Review

**Goal:** Audit Docker configuration

**Solution:**
```bash
# Docker-only scan
./scripts/security_scan.sh . --docker-only

# Or specific checks
grep -rn "^FROM.*:latest" . --include="Dockerfile*"
grep -rn "^USER root" . --include="Dockerfile*"
```

## 🔧 Advanced Usage

### Custom Entropy Thresholds

More sensitive (catches more, but more false positives):
```bash
python3 scripts/entropy_detector.py --min-entropy 4.0 --min-length 16
```

Less sensitive (higher confidence, fewer results):
```bash
python3 scripts/entropy_detector.py --min-entropy 5.5 --min-length 32
```

### Filtering Results

**JSON output for processing:**
```bash
python3 scripts/entropy_detector.py --format json | jq '.[] | select(.confidence == "High")'
```

**CSV for spreadsheets:**
```bash
python3 scripts/entropy_detector.py --format csv > results.csv
```

### Scanning Multiple Repositories

```bash
#!/bin/bash
for repo in ~/projects/*; do
  echo "Scanning $repo..."
  cd "$repo"
  ./path/to/security_scan.sh . --quick
done
```

### Integration with Git Hooks

**Pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
echo "Checking for secrets..."
if ! python3 scripts/entropy_detector.py --min-entropy 5.5; then
  echo "❌ Potential secrets detected! Commit blocked."
  exit 1
fi
echo "✓ No secrets detected"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Slack Integration

Send results to Slack:
```bash
#!/bin/bash
RESULT=$(./scripts/security_scan.sh . --full)
SCORE=$(echo "$RESULT" | grep "Security Score:" | cut -d: -f2)

curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"Security Audit Complete\nScore: $SCORE\"}" \
  $SLACK_WEBHOOK_URL
```

## 📈 Output Examples

### Entropy Detector Output

```
================================================================================
High-Entropy String Detection Results
================================================================================
Total potential secrets found: 3

High Confidence (1 findings)
--------------------------------------------------------------------------------

📍 src/config.py:12
   Entropy: 5.78 | Length: 40 | Confidence: High
   String: sk_live_4eC39HqLyjWDarjtT1zdp7dc
   Context: STRIPE_SECRET_KEY=sk_live_4eC39HqLyjWDarjtT1zdp7dc

Medium Confidence (2 findings)
...
```

### Security Scanner Output

```
============================================================
Security Audit Report
============================================================
Directory: /path/to/repo
Date: 2026-06-11

--- Credential & Secret Detection ---

[CRITICAL] AWS Access Keys detected:
src/aws.py:23: AWS_KEY = "AKIAIOSFODNN7EXAMPLE"

✓ No Google API Keys detected
✓ No Private Keys detected

--- Configuration Security ---

[HIGH] World-readable sensitive files detected:
./config/database.key (permissions: 644, should be 600)

✓ No SUID/SGID files

--- Container Security ---

[MEDIUM] Dockerfiles using :latest tag:
./Dockerfile:1: FROM ubuntu:latest

============================================================
Audit Summary
============================================================
Total Issues Found: 3

Critical: 1
High:     1
Medium:   1
Low:      0

Security Score: 70/100 (Grade: C)
Security Posture: Fair

⚠️  HIGH: Prompt remediation recommended
```

### Full Agent Report (via /security-audit)

See the example report I generated earlier - comprehensive Markdown with:
- Executive summary
- Risk matrix
- Detailed findings tables
- Compliance mapping
- Prioritized remediation plan

## 🛠️ Troubleshooting

### Issue: "Skill not found"

**Cause:** Skill not installed or Claude doesn't see it

**Solution:**
```bash
# Install the skill
cd security-auditor/skills
./install.sh --symlink

# Verify installation
ls -la ~/.claude/skills/security-audit.md

# Restart Claude Code
```

### Issue: "Permission denied"

**Cause:** Scripts not executable

**Solution:**
```bash
chmod +x scripts/entropy_detector.py
chmod +x scripts/security_scan.sh
chmod +x skills/install.sh
```

### Issue: "Agent failed to spawn"

**Cause:** Agent file not found or invalid

**Solution:**
```bash
# Check file exists
ls -la SKILL.md

# Verify YAML frontmatter
head -20 SKILL.md
```

### Issue: "Too many false positives"

**Cause:** Entropy threshold too low

**Solution:**
```bash
# Increase threshold
python3 scripts/entropy_detector.py --min-entropy 5.5

# Or use pattern matching only
./scripts/security_scan.sh . --secrets-only
```

## 📚 Learn More

- **Agent Specification:** `SKILL.md` - How the agent works
- **Architecture:** `references/ARCHITECTURE.md` - System design and data flow
- **Quick Reference:** `references/QUICKREF.md` - Command cheatsheet
- **Tools Documentation:** `scripts/README.md` - Standalone tools guide
- **Skills Documentation:** `skills/README.md` - Slash command guide

## 🎓 Best Practices

1. **Start with Quick Scan**
   - Use `--quick` for initial assessment
   - Full scan for comprehensive review

2. **Regular Audits**
   - Weekly full scans
   - Daily quick scans in CI/CD
   - Pre-commit entropy checks

3. **Review False Positives**
   - High confidence = investigate immediately
   - Medium confidence = review carefully
   - Low confidence = quick glance

4. **Incremental Remediation**
   - Fix critical issues first
   - High severity next
   - Medium/low as time allows

5. **Document Exceptions**
   - Add comments for legitimate "secrets" (example values)
   - Use .gitignore for generated files
   - Create suppression file for known false positives

6. **Share Results**
   - Include security score in PR descriptions
   - Track trends over time
   - Celebrate improvements

## 🚦 Decision Tree

```
Need to check for secrets?
├─ Yes, quickly → python3 scripts/entropy_detector.py
├─ Yes, comprehensive → ./scripts/security_scan.sh . --full
└─ Yes, with analysis → /security-audit

Need full security audit?
├─ Quick overview → /security-audit --quick
├─ Comprehensive → /security-audit
└─ With auto-fix → /security-audit --remediate

In CI/CD pipeline?
├─ Pre-commit → entropy_detector.py --min-entropy 5.5
├─ PR check → security_scan.sh . --quick
└─ Scheduled → security_scan.sh . --full

Learning/exploring?
└─ Ask Claude in natural language
```

## 💡 Pro Tips

1. **Combine Tools**
   ```bash
   # Quick entropy, then detailed scan if issues found
   python3 scripts/entropy_detector.py --format json > entropy.json
   if [ $(jq '. | length' entropy.json) -gt 0 ]; then
     ./scripts/security_scan.sh . --full
   fi
   ```

2. **Version Your Reports**
   ```bash
   ./scripts/security_scan.sh . --full > reports/audit-$(git rev-parse --short HEAD).md
   ```

3. **Track Improvements**
   ```bash
   # Compare scores over time
   echo "$(date),$(./scripts/security_scan.sh . --full | grep 'Security Score')" >> scores.csv
   ```

4. **Custom Patterns**
   Add your own secret patterns to the grep commands in `security_scan.sh`

5. **Whitelist Known Good**
   Modify `entropy_detector.py` to exclude specific strings or files

---

**Questions?** Check the documentation files or ask Claude!

**Contributions?** Improvements welcome! See `IMPROVEMENTS_SUMMARY.md` for ideas.

**Issues?** Review `ARCHITECTURE.md` to understand how components interact.

Happy auditing! 🔒✨
