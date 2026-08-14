# Security Audit Quick Reference

Quick reference for running security scans manually using the commands from the security-auditor skill.

## 🔍 Quick Scans

### Credential & Secret Detection

```bash
# Pattern-based secret search
grep -rInE "(password|passwd|pwd|secret|token|api_key|apikey|api-key|access_key|secret_key|private_key|client_secret|auth_token|bearer)\s*[:=]\s*['\"]?[a-zA-Z0-9/+=\-_]{8,}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} \
  --exclude="*.{min.js,map,lock,log}" 2>/dev/null

# AWS Keys
grep -rInE "AKIA[0-9A-Z]{16}" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null

# Google API Keys
grep -rInE "AIza[0-9A-Za-z\-_]{35}" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null

# GitHub Tokens
grep -rInE "gh[pousr]_[0-9a-zA-Z]{36,}" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null

# Private Keys
grep -rInE "BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null

# Entropy-based detection
python3 scripts/entropy_detector.py --min-entropy 4.5 --min-length 20
```

### Configuration Security

```bash
# World-readable sensitive files
find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name ".env" \) -perm -004 2>/dev/null

# World/group-writable configs
find . -type f \( -name "config.yml" -o -name "*.conf" \) -perm -022 2>/dev/null

# Executable config files
find . -type f \( -name "*.yml" -o -name "*.json" -o -name ".env*" \) -perm -111 2>/dev/null

# Files with SUID/SGID
find . -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null
```

### Container Security

```bash
# Find Dockerfiles with issues
grep -rn "^FROM.*:latest" . --include="Dockerfile*" 2>/dev/null  # Latest tag usage
grep -rn "^USER root" . --include="Dockerfile*" 2>/dev/null      # Root user

# No USER directive (runs as root)
for f in $(find . -name "Dockerfile*" 2>/dev/null); do
  grep -q "^USER " "$f" || echo "$f: No USER directive"
done

# Hardcoded secrets in Dockerfiles
grep -rInE "(ENV|ARG).*(PASSWORD|SECRET|KEY|TOKEN)\s*=" . --include="Dockerfile*" 2>/dev/null

# Docker Compose security
grep -n "privileged: true" docker-compose.y*ml 2>/dev/null
grep -n "network_mode:.*host" docker-compose.y*ml 2>/dev/null
```

## 📦 Dependency Scanning

### Python
```bash
# Find dependency files
find . -type f \( -name "requirements*.txt" -o -name "pyproject.toml" -o -name "Pipfile" \) 2>/dev/null

# List dependencies
cat requirements.txt 2>/dev/null
grep -A 100 '^\[tool.poetry.dependencies\]' pyproject.toml 2>/dev/null
```

### JavaScript/Node.js
```bash
# Find package.json
find . -name "package.json" -not -path "*/node_modules/*" 2>/dev/null

# Extract dependencies
cat package.json | grep -A 100 '"dependencies"' 2>/dev/null
```

### Java/Maven
```bash
# Find pom.xml
find . -name "pom.xml" 2>/dev/null

# Extract dependencies
grep -A 5 "<dependency>" pom.xml 2>/dev/null
```

### Docker
```bash
# Extract base images
grep "^FROM" Dockerfile 2>/dev/null
```

## 🛡️ Comprehensive Scan

Run a complete security scan:

```bash
#!/bin/bash

echo "=== Security Audit Report ==="
echo "Date: $(date)"
echo "Directory: $(pwd)"
echo ""

echo "--- Checking for Secrets ---"
echo "AWS Keys:"
grep -rInE "AKIA[0-9A-Z]{16}" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null | wc -l
echo "Private Keys:"
grep -rInE "BEGIN.*PRIVATE KEY" . --exclude-dir={.git,node_modules,vendor,venv} 2>/dev/null | wc -l
echo "High-Entropy Strings:"
python3 scripts/entropy_detector.py --format json 2>/dev/null | jq '. | length' 2>/dev/null || echo "0"

echo ""
echo "--- Configuration Issues ---"
echo "World-readable sensitive files:"
find . -type f \( -name "*.key" -o -name "*.pem" -o -name ".env" \) -perm -004 2>/dev/null | wc -l
echo "Writable configs:"
find . -type f -name "*.conf" -perm -022 2>/dev/null | wc -l

echo ""
echo "--- Container Security ---"
echo "Dockerfiles using :latest:"
grep -r "^FROM.*:latest" . --include="Dockerfile*" 2>/dev/null | wc -l
echo "Dockerfiles running as root:"
for f in $(find . -name "Dockerfile*" 2>/dev/null); do
  grep -q "^USER " "$f" || echo "$f"
done | wc -l

echo ""
echo "--- Dependencies ---"
echo "Python dependencies:"
find . -name "requirements.txt" -not -path "*/venv/*" 2>/dev/null | wc -l
echo "Node.js projects:"
find . -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | wc -l
echo "Java/Maven projects:"
find . -name "pom.xml" 2>/dev/null | wc -l

echo ""
echo "=== Scan Complete ==="
```

Save as `quick_security_scan.sh`, make executable with `chmod +x quick_security_scan.sh`, and run with `./quick_security_scan.sh`.

## 🎯 Priority Actions

### Critical (Do First)
1. Search for exposed API keys and tokens
2. Check for committed .env files
3. Scan for private keys in repository
4. Review world-readable sensitive files

### High Priority
1. Run entropy detector for unknown secrets
2. Check Docker images for hardcoded credentials
3. Review file permissions on config files
4. Scan dependencies for known CVEs

### Medium Priority
1. Review Docker best practices
2. Check for insecure cryptographic practices
3. Validate .gitignore completeness
4. Review access control implementations

## 📊 Interpreting Results

### Secret Detection
- **Pattern Match**: High confidence - investigate immediately
- **High Entropy (>5.5)**: Very likely a secret
- **Medium Entropy (4.5-5.5)**: Review context carefully
- **Low Entropy (<4.5)**: Likely false positive

### File Permissions
- **Sensitive files (keys, certs)**: Should be 600 (owner read/write only)
- **Config files**: Should be 644 (owner write, all read) or 600
- **Directories**: Should be 755 (rwxr-xr-x) at most
- **SUID/SGID on regular files**: Usually suspicious

### Container Issues
- **:latest tag**: Should pin to specific version
- **Running as root**: Should have USER directive
- **Hardcoded secrets**: Move to environment variables or secrets management
- **No HEALTHCHECK**: Add for production containers

## 🔧 Tools Integration

### Use with CI/CD

GitHub Actions:
```yaml
- name: Security Scan
  run: |
    python3 scripts/entropy_detector.py --format json > entropy_results.json
    if [ $(jq '. | length' entropy_results.json) -gt 0 ]; then
      echo "Secrets detected!"
      exit 1
    fi
```

GitLab CI:
```yaml
security_scan:
  script:
    - python3 scripts/entropy_detector.py
    - grep -rInE "AKIA[0-9A-Z]{16}" . --exclude-dir=.git
  allow_failure: false
```

## 📚 Additional Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- Docker Security: https://docs.docker.com/engine/security/
- Secret Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## 🤝 Getting Help

For issues or questions:
1. Check the Security Auditor Agent documentation in `security-auditor.md`
2. Review the tools README in `tools/README.md`
3. Run with `--help` flag for command-line tools
