# opencode-agents

Collection of AI agent skills following the [Agent Skills](https://agentskills.io/specification) specification. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter plus optional `references/` and `scripts/` subdirectories.

## Skills

| Skill | Directory | Version | Tools | Compatibility |
|-------|-----------|---------|-------|---------------|
| Security Auditor | `security-auditor/` | 1.2.0 | Bash, Read, Write, Edit, WebFetch, WebSearch | bash, python3, git |
| Git History Summarizer | `git-summary/` | 1.0.0 | Bash (git) | git |
| Wikipedia Deep Research | `wikipedia/` | 2.0.0 | Bash, WebFetch, WebSearch | network access |

## Key skill constraints

### Security Auditor (`security-auditor/`)
- **Default is read-only** — code modifications require `remediate: true`
- Bundled scripts in `scripts/`:
  - `entropy_detector.py` — Shannon entropy secret detection
  - `security_scan.sh` — comprehensive scanner (`--full`, `--quick`, `--secrets-only`, `--config-only`, `--docker-only`)
- Web fetch failures (CVE lookup) are non-critical — omit from report, don't fail the audit
- Scoring: 100 base, -40 critical, -20 high, -10 medium, -5 low -> A-F grade
- Always provide an absolute `repository_path`

### Git History Summarizer (`git-summary/`)
- Read-only — never modifies files
- Requires a valid git repository
- For repos with >10,000 commits, recommend setting `max_commits`

### Wikipedia Deep Research (`wikipedia/`)
- **`topic` parameter is mandatory** — agent must stop with error if missing
- Read-only — never modifies files
- Uses WebFetch for Wikipedia article content; WebSearch for topic discovery
- Rate-limit Wikipedia: 200 req/sec for API, implement respectful delays
- Handle disambiguation pages before attempting content extraction

## Structure

```
opencode-agents/
├── AGENTS.md
├── README.md
├── LICENSE
├── git-summary/
│   ├── SKILL.md
│   └── references/
│       ├── OUTPUT_FORMAT.md
│       └── REFERENCE.md
├── security-auditor/
│   ├── SKILL.md
│   ├── references/
│   │   ├── ARCHITECTURE.md
│   │   ├── DETAILED_SPEC.md
│   │   ├── OUTPUT_FORMAT.md
│   │   ├── QUICKREF.md
│   │   └── USAGE_GUIDE.md
│   └── scripts/
│       ├── entropy_detector.py
│       ├── security_scan.sh
│       └── README.md
└── wikipedia/
    ├── SKILL.md
    └── references/
        ├── OUTPUT_FORMAT.md
        └── REFERENCE.md
```

## No build/test/lint

This repo has no build system, tests, linters, or CI. All content is markdown except the executable scripts:
- `security-auditor/scripts/security_scan.sh`
- `security-auditor/scripts/entropy_detector.py`

## Writing new skills

Skills follow the [agentskills.io specification](https://agentskills.io/specification). Each skill directory must contain a `SKILL.md` with this frontmatter:

```yaml
---
name: skill-name          # must match directory name, lowercase + hyphens only
description: >-
  What the skill does and when to use it. Include keywords that help
  agents identify relevant tasks.
license: Apache-2.0
compatibility: Required tools and environment
metadata:
  author: mcaimi
  version: "1.0.0"
allowed-tools: Bash Read  # space-separated list
---
```

Keep `SKILL.md` under 500 lines. Move detailed reference material to `references/`, output format templates to `references/OUTPUT_FORMAT.md`, and executable code to `scripts/`.

## Common pitfalls

- **Security Auditor** will try to run WebSearch for CVE lookups — if it fails, continue with the rest of the report
- **Wikipedia Deep Research** must validate `topic` presence before any processing
- **Git History Summarizer** must not attempt file writes
- The `name` field in SKILL.md frontmatter must match the parent directory name exactly
