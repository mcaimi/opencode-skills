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

Perform network reconnaissance and port scanning using nmap. This skill covers the full
lifecycle: target validation, host discovery, firewall mapping, port scanning, service
enumeration, OS fingerprinting, vulnerability assessment, and structured reporting.

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

The user may request a scan by profile name or by specifying individual options. When a
profile is requested, use the corresponding nmap flags. When individual options are given,
compose the command from the [nmap reference](references/NMAP_REFERENCE.md).

### Quick Discovery

**Purpose**: Fast host discovery with minimal port checking.
**When to use**: "What's on this network?", "Find live hosts", "Quick scan".

```bash
nmap -sn -PE -PS80,443 -PA80,443 -PP -PU40125 --reason <target>
```

Use combined TCP SYN (`-PS`) and TCP ACK (`-PA`) probes together to maximize bypass
chances against both stateful and stateless firewalls. Add `-PU` for UDP probe diversity.

**Notes**:
- ARP scanning is automatic on local LAN segments and is fastest/most reliable. Proxy ARP
  can cause false positives; use `--disable-arp-ping` if this is suspected.
- Add `--traceroute` for network topology mapping when needed.
- On the Internet, `-PE` alone is unreliable — many hosts block ICMP echo. The combined
  probe approach compensates for this.
- For IPv6 targets, add `-6`. ICMP neighbor discovery replaces ARP on IPv6.

### Standard Scan

**Purpose**: Default balanced scan of common ports with service detection.
**When to use**: "Scan this host", "What ports are open?", no specific profile requested.

Privileged (root):
```bash
sudo nmap -sS -sV --version-intensity 5 -T4 --reason --open -oX - <target>
```

Unprivileged (non-root):
```bash
nmap -sT -sV --version-intensity 5 -T4 --reason --open -oX - <target>
```

Note: `-sT` (connect scan) performs a full TCP handshake (2x packets for open ports vs SYN
scan) and the connection is logged by target services in syslog. `-sT` is also required
for IPv6 scanning and when using `--proxies`.

### Comprehensive Scan

**Purpose**: Deep scan with OS detection, scripts, full port range, and traceroute.
**When to use**: "Full scan", "Deep scan", "Comprehensive assessment", "Thorough scan".

```bash
sudo nmap -sS -sU -sV -O --osscan-limit --osscan-guess -sC -p- -T4 \
  --traceroute --reason --open --host-timeout 30m --script-timeout 5m -oX - <target>
```

**Notes**:
- OS detection requires at least one open AND one closed TCP port for accurate
  fingerprinting. `--osscan-limit` skips hosts that don't meet this requirement,
  saving time. `--osscan-guess` provides best-effort matches with confidence percentages.
- `--host-timeout 30m` prevents slow hosts from consuming the majority of scan time.
- `--script-timeout 5m` prevents individual script hangs.
- Full port range UDP (`-sU -p-`) takes 18+ hours on Linux due to ICMP rate limiting.
  Consider a phased approach (see [Multi-Phase Scanning](#multi-phase-scanning-methodology)).

### Aggressive Recon

**Purpose**: Maximum information gathering on a single host or small group.
**When to use**: "Tell me everything", "Full recon", "Aggressive scan".

```bash
sudo nmap -A -T4 --reason --open -oX - <target>
```

The `-A` flag enables OS detection (`-O`), version detection (`-sV`), default script scan
(`-sC`), and traceroute (`--traceroute`) in one flag. Equivalent to running all of those
individually but more convenient for single-target deep dives.

### Stealth Scan

Stealth scanning is not a single profile but a graduated methodology. Choose the
appropriate level based on the threat model and IDS/IPS sophistication.

#### Level 1 — Low Profile (Basic IDS Evasion)

```bash
sudo nmap -sS -T2 -f --data-length 24 --randomize-hosts --reason --open -oX - <target>
```

Slower timing, fragmented packets, random payload padding. Effective against simple
threshold-based IDS.

#### Level 2 — Firewall Bypass (Non-Stateful Firewalls)

```bash
sudo nmap -sN -T2 --data-length 24 --randomize-hosts --reason -oX - <target>
```

NULL scan (`-sN`) sends packets with no TCP flags set. Exploits RFC 793: compliant stacks
drop the packet if the port is open, send RST if closed. Bypasses non-stateful firewalls
that only filter SYN packets (e.g., iptables `--syn` rules).

Alternatives: `-sF` (FIN only) or `-sX` (FIN+PSH+URG / Xmas tree).

**Critical limitation**: NULL/FIN/Xmas scans do NOT work against Windows, Cisco IOS,
IBM OS/400, or BSDI — these systems send RST for all ports regardless of state. Check
the target OS first. Results are always `open|filtered` (cannot distinguish).

#### Level 3 — Deep Evasion (IDS-Aware)

```bash
sudo nmap -sS -T1 -f -D RND:5,ME -g 53 --scan-delay 5s \
  --data-length 32 --randomize-hosts --spoof-mac 0 --reason --open -oX - <target>
```

- `-T1` (Sneaky): 15-second inter-probe delay defeats threshold-based IDS.
- `-D RND:5,ME`: Five random decoys with your real IP positioned among them. Decoy
  hosts must be alive to avoid SYN-flooding the target. Position `ME` sixth or later
  to hide from detectors like Scanlogd.
- `-g 53`: Spoof source port as DNS (53). Exploits misconfigured firewalls that
  allow all traffic from port 53 (also try 20 for FTP, 88 for Kerberos).
- `--spoof-mac 0`: Random MAC address (only works on same subnet).
- `--scan-delay 5s`: Explicit inter-probe delay to evade rate-based detection.

#### Level 4 — Maximum Stealth (Idle Scan)

```bash
sudo nmap -sI <zombie_host>:<probe_port> -Pn --reason -oX - <target>
```

Truly blind scan — no packets are sent from your real IP address. All probing is
performed through a "zombie" host by exploiting predictable IP ID sequences.

**Requirements**:
- Find a suitable zombie: `nmap --script ipidseq -p <port> <candidate_zombie>`
  Look for "Incremental" IP ID sequence class.
- Zombie must be idle (minimal traffic) to maintain predictable IP IDs.
- Must use `-Pn` to skip host discovery (which would expose your real IP).
- Performance: ~15x slower than direct SYN scan.

**Bonus**: Idle scan also reveals IP-based trust relationships — if the target firewall
allows traffic from the zombie's IP but not yours, idle scan will find those ports.

### Firewall Analysis

**Purpose**: Map firewall rules and determine filtering policies before deeper scanning.
**When to use**: "Map the firewall", "What's filtered?", "Firewall rules", pre-scan recon.

```bash
sudo nmap -sA -T4 --reason -oX - <target>
```

ACK scan never finds open ports directly. Instead it classifies ports as `filtered`
(no response or ICMP unreachable) or `unfiltered` (RST received). This reveals which
ports the firewall is actively blocking.

**Advanced — Combine with Window scan for deeper analysis**:

```bash
sudo nmap -sW -T4 --reason -oX - <target>
```

Window scan is identical to ACK scan but examines the TCP window size in RST responses.
Some systems use different window sizes for open vs closed ports, allowing single-scan
differentiation.

**Multi-Scan Correlation** (see [Methodology](#multi-scan-correlation)):
1. FIN scan → ports show `open|filtered`
2. ACK scan → ports show `filtered` vs `unfiltered`
3. Correlate: `open|filtered` (FIN) + `unfiltered` (ACK) = **open**

### SCTP Scan

**Purpose**: Scan SCTP ports used in telecom/SS7/SIGTRAN infrastructure.
**When to use**: "Scan SCTP", "Check SIGTRAN", "Telecom infrastructure scan".

```bash
sudo nmap -sY -T4 --reason --open -oX - <target>
```

SCTP INIT scan (`-sY`) is the SCTP equivalent of a TCP SYN scan — half-open, does not
complete the four-way handshake. For more stealth, use COOKIE ECHO scan (`-sZ`), which
cannot distinguish `open` from `filtered` but is less likely to be logged.

### Protocol Discovery

**Purpose**: Determine which IP protocols (not ports) a host supports.
**When to use**: "What protocols does this host support?", "Protocol scan", device profiling.

```bash
sudo nmap -sO --reason -oX - <target>
```

Reveals supported IP protocols (TCP, UDP, ICMP, IGMP, GRE, ESP, etc.). Useful for:
- **Device profiling**: End hosts typically support TCP/UDP/ICMP. Routers add GRE/EGP.
  VPN gateways add ESP/AH (IPsec).
- **Attack surface mapping**: Every supported protocol is a potential vector.
- **Network equipment identification**: Before deeper port scanning.

### UDP Scan

**Purpose**: Scan UDP ports (DNS, SNMP, DHCP, NTP, etc.).
**When to use**: "Scan UDP", "Check UDP services".

```bash
sudo nmap -sU --top-ports 100 -sV --version-intensity 0 -T4 \
  --reason --open -oX - <target>
```

**Performance notes** (UDP scanning is inherently slow):
- Linux kernels rate-limit ICMP port-unreachable to 1/second. A full 65,536-port UDP
  scan takes **18+ hours** per host.
- `--version-intensity 0` drastically reduces scan time (from ~1 hour to ~13 seconds in
  nmap documentation examples) while still sending protocol-specific payloads for common
  services.
- Nmap automatically sends protocol-appropriate payloads for well-known UDP services
  (DNS, SNMP, DHCP, TFTP, NTP) rather than empty packets.

**For full UDP coverage, use a phased approach**:
1. Fast scan: `-sU -F -sV --version-intensity 0` (top 100 ports)
2. Background sweep: `-sU -p- --defeat-icmp-ratelimit --host-timeout 15m`

**Combine with TCP** for comprehensive coverage:
```bash
sudo nmap -sU -sS --top-ports 100 -sV --version-intensity 2 -T4 \
  --reason --open -oX - <target>
```

**Distinguishing open vs filtered** (UDP's hardest problem):
- Add `-sV` — version detection sends service-specific probes that elicit responses.
- Compare traceroute hop counts: fewer hops to `open|filtered` vs `closed` ports
  may indicate the port is actually open (packet reached host but no ICMP response).

### Vulnerability Scan

**Purpose**: Script-based vulnerability assessment on discovered services.
**When to use**: "Check for vulnerabilities", "Vuln scan", "Security assessment".

```bash
sudo nmap -sS -sV -O --script=vuln,safe -T4 --reason --open -oX - <target>
```

**NSE Script Categories**:

| Category | Risk | Description |
|---|---|---|
| `default` / `-sC` | Safe | Useful scripts run by default |
| `safe` | Safe | Unlikely to crash targets |
| `vuln` | Safe | Check for known vulnerabilities |
| `auth` | Low | Authentication-related checks |
| `discovery` | Low | Network/service discovery |
| `broadcast` | Low | LAN broadcast-based discovery |
| `intrusive` | Medium | May crash targets or be detected |
| `brute` | High | Brute-force credential attacks |
| `exploit` | **Dangerous** | Actively exploit vulnerabilities |
| `dos` | **Dangerous** | Denial of service tests |

**Script selection with boolean expressions**:
```bash
--script="(default or safe or vuln) and not http-*"
--script="http-* and not (dos or exploit)"
```

**Authenticated checks** — pass credentials via `--script-args`:
```bash
--script-args 'user=admin,pass=secret'
--script-args-file creds.txt
```

**Warning**: NSE scripts are NOT sandboxed. The `exploit` and `dos` categories can damage
targets. Only use with explicit authorization and understanding of impact.

### Web Application Scan

**Purpose**: HTTP/HTTPS-focused service enumeration and vulnerability checks.
**When to use**: "Scan web services", "Check web apps", "Web security scan".

```bash
nmap -sV -p 80,443,8080,8443 --script="http-* and safe" -T4 \
  --reason --open -oX - <target>
```

**Useful HTTP scripts** (add individually as needed):
- `http-title`: Page titles for quick identification
- `http-headers`: Response headers analysis
- `http-methods`: Allowed HTTP methods (PUT, DELETE, etc.)
- `http-enum`: Common directory/file enumeration
- `http-sql-injection`: Basic SQL injection checks
- `http-csrf`: CSRF vulnerability detection
- `http-robots.txt`: Parse robots.txt for hidden paths

Use the `+` prefix to force a script to run even when the service is not auto-detected:
```bash
--script="+http-title"
```

### Infrastructure Discovery

**Purpose**: Broad network and service discovery using broadcast and SNMP.
**When to use**: "Map the infrastructure", "What devices are on this network?", "Network inventory".

```bash
nmap -sn --script=broadcast,discovery -e <interface> --reason <target>
```

Discovers services via LAN broadcast protocols (mDNS, UPnP, DHCP, NetBIOS, etc.).
Combine with SNMP enumeration for managed devices:

```bash
nmap -sU -p 161 --script=snmp-info,snmp-interfaces,snmp-sysdescr \
  --script-args snmpcommunity=public -T4 --reason --open -oX - <target>
```

### Custom Scan

When the user specifies individual flags or scan types, build the command from the
[nmap reference](references/NMAP_REFERENCE.md). Always include `--reason --open -oX -`
for parseable output unless the user explicitly requests otherwise.

**Custom TCP flags** (`--scanflags`): Combine arbitrary flags for evasion:
```bash
sudo nmap --scanflags SYNFIN -T4 --reason -oX - <target>
```
SYN/FIN combinations bypass firewalls that only block pure SYN packets. Over half of
OS fingerprints respond to SYN/FIN/URG/PSH combinations. Custom flag scans also evade
IDS that only pattern-match known nmap scan types.

## Operational Methodologies

### Multi-Phase Scanning Methodology

For large networks or thorough assessments, use a phased approach rather than a single
monolithic scan:

**Phase 1 — Firewall Mapping** (optional, for hardened targets):
```bash
sudo nmap -sA -T4 --reason -oX - <target_network>
```
Understand filtering rules before investing time in deep scans.

**Phase 2 — Host Discovery**:
```bash
nmap -sn -PE -PS80,443 -PA80,443 -PP -PU40125 --reason <target_network>
```
Identify live hosts. Save the list for subsequent phases.

**Phase 3 — Quick Port Survey**:
```bash
sudo nmap -sS --top-ports 1000 -T4 --reason --open -oX - -iL live_hosts.txt
```
Fast scan of common ports on discovered hosts.

**Phase 4 — Deep Scan on Interesting Hosts**:
```bash
sudo nmap -sS -sU -p- -sV -T4 --host-timeout 30m --reason --open -oX - <interesting_hosts>
```
Full port range with service detection on hosts that showed interesting results.

**Phase 5 — OS Fingerprinting and Scripts**:
```bash
sudo nmap -O --osscan-limit --osscan-guess -sC --script=vuln,safe \
  --reason --open -oX - <interesting_hosts>
```
Targeted fingerprinting and vulnerability checks on priority targets.

### Multi-Scan Correlation

Some port states cannot be determined by a single scan technique. Combine results
from different scans to reach definitive conclusions:

**Pattern: FIN + ACK correlation**
1. Run FIN scan: `sudo nmap -sF -T4 --reason -oX - <target>`
   - Open ports → `open|filtered` (no response)
   - Closed ports → `closed` (RST received)
2. Run ACK scan: `sudo nmap -sA -T4 --reason -oX - <target>`
   - Unfiltered ports → `unfiltered` (RST received regardless of open/closed)
   - Filtered ports → `filtered` (no response or ICMP unreachable)
3. Correlate results:
   - `open|filtered` (FIN) + `unfiltered` (ACK) = **open**
   - `open|filtered` (FIN) + `filtered` (ACK) = **filtered**
   - `closed` (FIN) + `unfiltered` (ACK) = **closed**

This technique is essential when stateful firewalls block SYN scans but allow other
TCP flag combinations through.

### Performance Optimization

**Version detection is the largest time sink.** Omitting `-sV` or reducing
`--version-intensity` is far more effective than adjusting timing templates.

**RTT-based tuning** for known network conditions:
- Ping the target first and note the maximum RTT.
- Set `--initial-rtt-timeout` to 2x the observed RTT.
- Set `--max-rtt-timeout` to 3-4x the observed RTT. Never below 100ms.

**Host group sizing** for network scans:
- For /24 networks: `--min-hostgroup 256` processes the entire subnet at once.
- For few-port scans: `--min-hostgroup 2048` or higher improves throughput.

**Retry tuning**:
- Reliable networks: `--max-retries 3` (default is 10).
- Informal surveys: `--max-retries 0` (fastest but may miss filtered ports).

**Slow host management**:
- `--host-timeout 30m` abandons hosts that take too long. The slowest few percent
  of hosts often consume the majority of total scan time.

**Rate control**:
- `--min-rate 100` guarantees minimum packet rate.
- `--max-rate 300` caps rate to avoid triggering IDS or overwhelming targets.
- Caution: higher rate can cause *longer* scans due to congestion-triggered retransmissions.

**UDP-specific optimization**:
- `--defeat-icmp-ratelimit`: Marks rate-limited ports as `open` instead of
  `open|filtered`. Faster but less accurate.
- `--scan-delay 1s`: Match the host's ICMP rate limit explicitly.
- `--min-hostgroup 100`: Amortize rate limiting across multiple hosts in parallel.

**DNS optimization**:
- `-n`: Skip reverse DNS resolution — significant speed improvement.
- `--dns-servers <srv>`: Use custom DNS for authoritative/faster resolution.
- Scan for port 53 on private networks first to find usable local DNS servers.

### Scan Resumption

Long-running scans can be resumed if interrupted. This requires file-based output
(not stdout):

```bash
sudo nmap -sS -p- -oN scan_progress.nmap -oX scan_results.xml <target>
# If interrupted (Ctrl+C or timeout):
sudo nmap --resume scan_progress.nmap
```

`--resume` only works with normal output (`-oN`) or grepable output (`-oG`), not XML.
For critical long-running scans, always use `-oA <basename>` to save all formats and
enable resumption.

### Runtime Interaction

During a running scan, nmap accepts keyboard input:
- `v` / `V`: Increase/decrease verbosity
- `d` / `D`: Increase/decrease debug level
- `p` / `P`: Turn on/off packet tracing
- Any other key: Print status line

For automated/scripted execution, use `--noninteractive` to disable these controls
and prevent accidental input from affecting the scan.

## Execution

### Target Specification

nmap accepts targets in these forms:
- Single host: `192.168.1.1` or `scanme.nmap.org`
- CIDR: `192.168.1.0/24`
- Range: `192.168.1.1-254`
- Octet range: `192.168.1,2,3.0/24`
- Input file: `-iL targets.txt`
- IPv6: `-6 fe80::1`
- Exclude: `--exclude <host1,host2>` or `--excludefile exclusions.txt`
- Random targets: `-iR <count>` (Internet-wide surveys)
- Deduplicate overlapping specs: `--unique`
- Resolve all IPs for a hostname: `--resolve-all`

Validate target format before scanning. Reject any target that looks like a production
system or public service the user likely does not own, unless authorization is confirmed.

### Privilege Handling

| Scan Feature | Requires Root |
|---|---|
| SYN scan (`-sS`) | Yes |
| UDP scan (`-sU`) | Yes |
| OS detection (`-O`) | Yes |
| NULL/FIN/Xmas (`-sN/-sF/-sX`) | Yes |
| ACK/Window scan (`-sA/-sW`) | Yes |
| SCTP scans (`-sY/-sZ`) | Yes |
| Idle scan (`-sI`) | Yes |
| IP Protocol scan (`-sO`) | Yes |
| TCP connect (`-sT`) | No |
| Service detection (`-sV`) | No |
| Script scan (`-sC`) | Depends on script |

If root is required and not available:
1. Prepend `sudo` and inform the user
2. Or fall back to unprivileged equivalents (e.g., `-sT` instead of `-sS`)

### Running the Scan

1. Build the nmap command based on profile or user options
2. Always append `--reason` for diagnostic clarity
3. Always append `-oX -` to get XML output on stdout for parsing
4. Capture both stdout and stderr
5. Parse the XML output to extract structured results

Use the parsing script:

```bash
nmap ... -oX - | python3 scripts/parse_nmap_xml.py -
```

Or for file-based output (supports resumption):

```bash
sudo nmap ... -oA scan_results <target>
python3 scripts/parse_nmap_xml.py scan_results.xml
```

The XML output from `-oX` contains all structured data needed for reporting, including
CPE identifiers, traceroute data, OS class details, and script output.

### Handling Long Scans

For scans expected to take a long time (full port range, large networks, UDP scans):

1. Inform the user of the expected duration
2. Use `--stats-every 30s` for progress updates
3. Use `-oA <basename>` (not `-oX -`) to enable `--resume` on interruption
4. For very large scans, use the [multi-phase methodology](#multi-phase-scanning-methodology)
5. Set `--host-timeout 30m` to prevent slow hosts from dominating scan time

## Output and Reporting

Generate a structured Markdown report. See [output format](references/OUTPUT_FORMAT.md)
for the full template.

### Report Sections

1. **Scan Summary**: Target, profile, timestamp, nmap version, scan duration
2. **Host Discovery**: Hosts up/down, hostnames, MAC addresses
3. **Port Findings**: Per-host table of open ports, services, versions, CPE identifiers
4. **Ambiguous States**: Ports in `open|filtered` or `closed|filtered` states with analysis
5. **OS Detection**: Identified operating systems with confidence, device type, vendor
6. **Firewall Analysis**: Filtered vs unfiltered ports, stateful/stateless determination
7. **Network Topology**: Traceroute results, hop counts, network path analysis
8. **Script Results**: Any script findings with CVE references
9. **Scan Coverage**: What was scanned (ports, protocols, phases) and what was not
10. **Risk Assessment**: Severity ratings for findings
11. **Recommendations**: Actionable remediation steps

### Risk Rating

Rate each finding:

| Rating | Criteria |
|---|---|
| **Critical** | Known exploitable vulnerability, default credentials, unauth RCE |
| **High** | Dangerous service exposed (telnet, rlogin, unencrypted admin), known CVE |
| **Medium** | Unnecessary service exposed, outdated version, weak config |
| **Low** | Information disclosure, minor misconfiguration |
| **Info** | Neutral observation, expected services |

### Key Patterns to Flag

- Unencrypted protocols where encrypted alternatives exist (HTTP vs HTTPS, Telnet vs SSH, FTP vs SFTP)
- Database ports exposed to non-private networks (3306, 5432, 27017, 6379)
- Administrative interfaces exposed (management consoles, debug ports)
- End-of-life software versions with known CVEs
- Default or commonly-exploited services (SMB, RDP with weak config)
- Services running on non-standard ports (possible evasion attempt or misconfiguration)
- SCTP services on telecom infrastructure (SS7/SIGTRAN exposure)
- Supported IP protocols beyond TCP/UDP/ICMP on endpoints (unexpected GRE, ESP, etc.)
- Weak TCP sequence prediction (enables IP spoofing attacks)
- Missing or misconfigured firewall rules (ports unfiltered that should be filtered)

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
