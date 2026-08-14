# opencode-agents

A collection of AI agent skills following the [Agent Skills specification](https://agentskills.io/specification). These skills extend AI coding agents with security auditing, git history analysis, and deep research from Wikipedia.

## Skills

### Security Auditor

A comprehensive security analysis skill that scans codebases for vulnerabilities, leaked credentials, misconfigurations, and dependency issues.

**Capabilities:**
- **Credential & Secret Detection** — Pattern-based matching (AWS keys, GitHub tokens, JWTs, private keys) combined with Shannon entropy analysis for unknown secrets
- **Configuration Security** — File permission audits, unencrypted key detection, SUID/SGID checks, .gitignore validation
- **Container Security** — Dockerfile best practices, docker-compose validation, base image analysis, Trivy integration
- **Code Security Analysis** — Injection vulnerabilities, insecure cryptography, CWE/OWASP Top 10 mapping
- **Dependency Vulnerabilities** — Auto-detection across 10+ languages (Python, JavaScript, Java, Go, Rust, etc.), CVE lookup with CVSS scoring
- **Git History Analysis** — Suspicious commit pattern detection, contributor statistics, activity anomalies
- **Auto-Remediation** — Optionally fix discovered issues directly in the codebase
- **Security Scoring** — A-F letter grade with point deductions per severity level
- **Compliance Mapping** — OWASP Top 10, CWE Top 25, SANS Top 25

**File structure:**
```
security-auditor/
├── SKILL.md
├── references/
│   ├── ARCHITECTURE.md
│   ├── DETAILED_SPEC.md
│   ├── OUTPUT_FORMAT.md
│   ├── QUICKREF.md
│   └── USAGE_GUIDE.md
└── scripts/
    ├── entropy_detector.py
    ├── security_scan.sh
    └── README.md
```

### Git History Summarizer

Analyzes git repository histories and produces comprehensive, structured summaries of commits, changes, and development patterns.

**Capabilities:**
- Full history or limited commit analysis (configurable N)
- Commit metadata extraction (author, timestamp, messages, diffs)
- Change pattern detection and file impact analysis
- Branch tracking and author statistics
- Time-based activity insights (peak days, hours, averages)
- Multiple output formats (Markdown, JSON)
- Filtering by author, date range, branch, or specific files

**File structure:**
```
git-summary/
├── SKILL.md
└── references/
    ├── OUTPUT_FORMAT.md
    └── REFERENCE.md
```

### Wikipedia Deep Research

Conducts comprehensive research on Wikipedia topics with multi-source aggregation and structured output.

**Capabilities:**
- **Deep Topic Analysis** — Full article extraction with section-by-section synthesis
- **Related Links Discovery** — Categorized into primary, secondary, broader context, and deeper dives
- **Citation Quality Assessment** — Multi-criteria scoring (credibility, recency, academic rigor)
- **Visual Content Extraction** — Images, diagrams, charts with full metadata and license compliance
- **Concept Mapping** — Generated visual graphs in Mermaid, Graphviz, JSON, or Cytoscape formats
- **Custom Summaries** — LLM-powered summaries with configurable style (academic, journalistic, ELI5, technical) and length
- **Interactive Refinement** — Conversational follow-up with expand, focus, compare, and clarify actions
- **Multi-language** — Support for any Wikipedia language edition
- **Configurable Depth** — Standard (5 links), comprehensive (10 links), or exhaustive (20 links)

**File structure:**
```
wikipedia/
├── SKILL.md
└── references/
    ├── OUTPUT_FORMAT.md
    └── REFERENCE.md
```

---

## Installation & Usage

These skills work with any agent that supports the [Agent Skills](https://agentskills.io) format. Below are instructions for the two primary targets.

### Claude Code

Claude Code looks for skills in two locations:

| Scope | Path | Applies to |
|-------|------|------------|
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | Current project only |

**Install all skills globally (symlink):**

```bash
# Clone the repo
git clone https://github.com/mcaimi/opencode-agents.git ~/opencode-agents

# Symlink each skill into your personal skills directory
ln -s ~/opencode-agents/git-summary ~/.claude/skills/git-summary
ln -s ~/opencode-agents/security-auditor ~/.claude/skills/security-auditor
ln -s ~/opencode-agents/wikipedia ~/.claude/skills/wikipedia
```

**Install a single skill into a project:**

```bash
# From your project root
mkdir -p .claude/skills
ln -s /path/to/opencode-agents/security-auditor .claude/skills/security-auditor
```

**Usage:** Skills activate automatically when Claude detects a relevant request, or you can invoke them directly:

```
/security-auditor    Run a security audit on the current repository
/git-summary         Summarize git history
/wikipedia           Research a topic on Wikipedia
```

Claude Code picks up new and modified skills without a restart (live change detection).

### OpenCode

OpenCode searches multiple paths for skills:

| Scope | Paths searched |
|-------|---------------|
| Project | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` |
| Global | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` |

**Install all skills globally:**

```bash
# Clone the repo
git clone https://github.com/mcaimi/opencode-agents.git ~/opencode-agents

# Symlink each skill (using any of the global paths)
ln -s ~/opencode-agents/git-summary ~/.config/opencode/skills/git-summary
ln -s ~/opencode-agents/security-auditor ~/.config/opencode/skills/security-auditor
ln -s ~/opencode-agents/wikipedia ~/.config/opencode/skills/wikipedia
```

**Install into a specific project:**

```bash
# From your project root
mkdir -p .opencode/skills
ln -s /path/to/opencode-agents/security-auditor .opencode/skills/security-auditor
```

Skills are auto-discovered from the filesystem. OpenCode loads skill descriptions at startup and activates the full instructions on demand.

**Permission control** (optional) in `opencode.json`:

```json
{
  "permission": {
    "skill": {
      "*": "allow"
    }
  }
}
```

Values: `"allow"` (load immediately), `"ask"` (prompt before loading), `"deny"` (hidden from agent).

### Other compatible agents

These skills work with any agent that supports the [agentskills.io specification](https://agentskills.io/specification), including Cursor, VS Code (GitHub Copilot), Gemini CLI, Roo Code, and others listed in the [client showcase](https://agentskills.io/clients). Check your agent's documentation for the skills directory path (commonly `.agents/skills/`).

---

## Skill Format

All skills follow the [agentskills.io specification](https://agentskills.io/specification). Each skill is a directory containing:

- **`SKILL.md`** (required) — YAML frontmatter with metadata (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) followed by markdown instructions
- **`references/`** (optional) — Detailed documentation, output format templates, and technical references loaded on demand
- **`scripts/`** (optional) — Executable code the agent can run (bash, python, etc.)

The `name` field in frontmatter must match the directory name. Skills are designed for progressive disclosure: metadata loads at startup, instructions load on activation, and reference files load only when needed.

## Project Structure

```
opencode-agents/
├── AGENTS.md
├── README.md
├── LICENSE
├── git-summary/
│   ├── SKILL.md
│   └── references/
├── security-auditor/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
└── wikipedia/
    ├── SKILL.md
    └── references/
```

---

## License

This project is licensed under the [GNU General Public License v3](LICENSE).
