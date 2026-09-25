---
name: port-scanner
description: >-
  Network port scanner and host discovery tool using nmap. Performs host discovery,
  TCP/UDP/SCTP port scanning, service version detection, OS fingerprinting, firewall
  analysis, and vulnerability assessment. Use when asked to scan a network, discover hosts,
  check open ports, identify running services, detect operating systems, map firewall rules,
  assess network security posture, or perform authorized penetration testing reconnaissance.
  Generates structured Markdown reports with findings, risk ratings, and remediation guidance.
license: Apache-2.0
compatibility: >-
  Requires nmap installed and accessible in PATH. Some scan types (SYN, OS detection,
  raw packet crafting) require root/sudo privileges. Designed for Claude Code or similar
  agentic coding assistants.
metadata:
  author: opencode-skills
  version: "2.0"
allowed-tools: Bash(nmap:*) Bash(sudo:*) Bash(which:*) Bash(grep:*) Bash(awk:*) Bash(sort:*) Bash(xmllint:*) Bash(python3:*) Read Write
---

# Port Scanner Skill

Perform network reconnaissance and port scanning using nmap. Select a scan profile
below, then follow the execution flow to run the scan and generate a report.

## Authorization Gate

**MANDATORY**: Before executing any scan, confirm that the operator has explicit written
authorization to scan the target. If authorization is unclear, ask before proceeding.
Never scan targets without confirmed authorization. This is a legal requirement.

Prompt the user:

> Before I scan `<target>`, please confirm you have written authorization to scan this
> host/network. Unauthorized scanning may violate computer crime laws. Do you confirm?

Skip this prompt only if the user has already confirmed authorization in this conversation
or if the target is `localhost` / `127.0.0.1` / `::1` / a private RFC 1918 address that
the user owns.

## Prerequisites Check

Before scanning, verify nmap is installed:

```bash
which nmap && nmap --version
```

If nmap is not found, inform the user and suggest installation:
- macOS: `brew install nmap`
- Debian/Ubuntu: `sudo apt-get install nmap`
- RHEL/Fedora: `sudo dnf install nmap`
- Arch: `sudo pacman -S nmap`

Check if running with privileges (needed for SYN scans, OS detection):

```bash
id -u
```

If UID is not 0 and the requested scan requires privileges, inform the user that `sudo`
will be needed and ask for confirmation.

## Scan Profiles

Select the profile matching the user's request, then read its details from
[scan profiles](references/SCAN_PROFILES.md). When individual nmap flags are specified
instead of a profile, compose the command from the [nmap reference](references/NMAP_REFERENCE.md).

| Profile | When to use | Privileges |
|---|---|---|
| Quick Discovery | "What's on this network?", find live hosts, quick scan | No |
| Standard Scan | Default — "What ports are open?", no specific profile requested | Preferred |
| Comprehensive Scan | "Full scan", "Deep scan", "Thorough scan" | Yes |
| Aggressive Recon | "Tell me everything", "Full recon" | Yes |
| Stealth Scan (L1-L4) | IDS/firewall evasion, graduated stealth levels | Yes |
| Firewall Analysis | "Map the firewall", "What's filtered?" | Yes |
| SCTP Scan | "Scan SCTP", telecom/SIGTRAN infrastructure | Yes |
| Protocol Discovery | "What protocols?", device profiling | Yes |
| UDP Scan | "Scan UDP", "Check UDP services" | Yes |
| Vulnerability Scan | "Check for vulnerabilities", "Security assessment" | Yes |
| Web Application Scan | "Scan web services", "Check web apps" | No |
| Infrastructure Discovery | "Map the infrastructure", "Network inventory" | No |
| Custom Scan | User specifies individual nmap flags | Depends |

For multi-phase scanning, scan correlation, or performance tuning, see
[methodologies](references/METHODOLOGIES.md).

## Execution

### Target Validation

Validate target format before scanning. Reject any target that looks like a production
system or public service the user likely does not own, unless authorization is confirmed.
For target specification syntax, see [nmap reference](references/NMAP_REFERENCE.md).

### Privilege Handling

| Scan Feature | Requires Root |
|---|---|
| SYN scan (`-sS`), UDP (`-sU`), OS detection (`-O`) | Yes |
| NULL/FIN/Xmas (`-sN/-sF/-sX`), ACK/Window (`-sA/-sW`) | Yes |
| SCTP (`-sY/-sZ`), Idle (`-sI`), Protocol (`-sO`) | Yes |
| TCP connect (`-sT`), Service detection (`-sV`) | No |

If root is required and not available, prepend `sudo` and inform the user, or fall back
to unprivileged equivalents (e.g., `-sT` instead of `-sS`).

### Running the Scan

1. Build the nmap command based on the selected profile
2. Always append `--reason` for diagnostic clarity
3. Always append `-oX -` to get XML output on stdout for parsing
4. Pipe output through the parser:

```bash
nmap ... -oX - | python3 scripts/parse_nmap_xml.py -
```

For scans needing resumption support, use file-based output instead:

```bash
sudo nmap ... -oA scan_results <target>
python3 scripts/parse_nmap_xml.py scan_results.xml
```

### Handling Long Scans

For scans expected to take a long time (full port range, large networks, UDP scans):

1. Inform the user of the expected duration
2. Use `--stats-every 30s` for progress updates
3. Use `-oA <basename>` (not `-oX -`) to enable `--resume` on interruption
4. For very large scans, use the [multi-phase methodology](references/METHODOLOGIES.md#multi-phase-scanning-methodology)
5. Set `--host-timeout 30m` to prevent slow hosts from dominating scan time

## Error Handling

| Error | Action |
|---|---|
| nmap not found | Suggest installation, abort |
| Permission denied | Suggest sudo or fall back to unprivileged scan |
| Host unreachable | Report as down, suggest `-Pn` if host is expected to be up |
| Network unreachable | Check interface, suggest `-e <iface>` |
| Timeout | Report partial results, suggest `-T3` or `--host-timeout` increase |
| DNS resolution failure | Suggest `-n` to skip DNS, or check target hostname |
| Scan interrupted | Suggest `--resume` if `-oN`/`-oG` output was used |
| Rate limiting detected | Suggest `--scan-delay`, reduce `-T` level, or use `--defeat-icmp-ratelimit` |
| Zombie unsuitable (idle scan) | IP ID not incremental; find another zombie candidate |
| NULL/FIN/Xmas all closed | Target OS likely Windows/Cisco; fall back to SYN or connect scan |

## Reporting

Generate a structured Markdown report following the [output format](references/OUTPUT_FORMAT.md).
Rate each finding using the risk criteria defined in that reference. Flag the
[key patterns](references/OUTPUT_FORMAT.md#key-patterns-to-flag) when detected.
