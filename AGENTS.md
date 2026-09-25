# opencode-agents

Collection of AI agent skills following the [Agent Skills](https://agentskills.io/specification) specification. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter plus optional `references/` and `scripts/` subdirectories.

## Skills

| Skill | Directory | Version | Tools | Compatibility |
|-------|-----------|---------|-------|---------------|
| Security Auditor | `security-auditor/` | 1.2.0 | Bash, Read, Write, Edit, WebFetch, WebSearch | bash, python3, git |
| Git History Summarizer | `git-summary/` | 1.0.0 | Bash (git) | git |
| Memory Cube | `memory-cube/` | 1.1.0 | Bash (python3, cat, ls, rm), Read, Write, Edit | python3, patch |
| Port Scanner | `port-scanner/` | 2.0 | Bash (nmap, sudo, which, grep, awk, sort, xmllint, python3), Read, Write | nmap |
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

### Memory Cube (`memory-cube/`)
- Two banks: `memory` (factual knowledge, explicit user request only) and `personality` (agent behavior, proactively offered)
- Storage at `~/.memory_cube/memory` and `~/.memory_cube/personality`
- Scripts in `scripts/`:
  - `memory-content.py` — list/search memories (`--search`, `--bank`, `--format`, `--limit`)
  - `memorize.py` — write/append/diff-patch memories (`--stdin`, `--append`, `--diff`, `-o FILE`, `--bank`)
- File format: `CATEGORY-SUBTOPIC.md` with YAML frontmatter (`topic`, `category`, `summary`, `saved_from`)
- Strip or mask secrets before saving — warn the user
- `-o` filename must be plain (no path traversal with `../`)

### Port Scanner (`port-scanner/`)
- **Authorization gate is mandatory** — must confirm written authorization before scanning any target
- Exception: `localhost` / `127.0.0.1` / `::1` / private RFC 1918 addresses the user owns
- Some scans require root/sudo: SYN (`-sS`), UDP (`-sU`), OS detection (`-O`), NULL/FIN/Xmas, SCTP, idle scan
- Unprivileged fallback: use `-sT` (TCP connect) instead of `-sS` (SYN)
- Scripts in `scripts/`:
  - `parse_nmap_xml.py` — parses nmap XML output into structured Markdown
- Always append `--reason` and `-oX -` to nmap commands for parsing
- Long scans: use `--stats-every 30s`, `-oA <basename>` for resume support, `--host-timeout 30m`
- 13 scan profiles from Quick Discovery to Vulnerability Scan (see `references/SCAN_PROFILES.md`)

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
├── memory-cube/
│   ├── SKILL.md
│   ├── references/
│   │   ├── NAMING_AND_FORMAT.md
│   │   └── REFERENCE.md
│   └── scripts/
│       ├── memorize.py
│       └── memory-content.py
├── port-scanner/
│   ├── SKILL.md
│   ├── references/
│   │   ├── METHODOLOGIES.md
│   │   ├── NMAP_REFERENCE.md
│   │   ├── OUTPUT_FORMAT.md
│   │   └── SCAN_PROFILES.md
│   └── scripts/
│       └── parse_nmap_xml.py
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
- `memory-cube/scripts/memorize.py`
- `memory-cube/scripts/memory-content.py`
- `port-scanner/scripts/parse_nmap_xml.py`
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

- **Memory Cube** personality entries must not duplicate — update or replace existing entries instead of creating new ones
- **Memory Cube** `-o` filenames must be plain names (no `../` path traversal); secrets must be stripped before saving
- **Port Scanner** must always confirm authorization before scanning — never skip the authorization gate
- **Port Scanner** scans requiring root will fail silently or produce incomplete results without `sudo`
- **Security Auditor** will try to run WebSearch for CVE lookups — if it fails, continue with the rest of the report
- **Wikipedia Deep Research** must validate `topic` presence before any processing
- **Git History Summarizer** must not attempt file writes
- The `name` field in SKILL.md frontmatter must match the parent directory name exactly
