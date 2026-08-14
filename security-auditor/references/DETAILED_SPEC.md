# Detailed Detection Commands

Complete reference of all detection commands used by the security auditor.

## Credential Detection Patterns

### Pattern-Based Detection

```bash
# Generic secret patterns
grep -rInE "(password|passwd|pwd|secret|token|api_key|apikey|api-key|access_key|secret_key|private_key|client_secret|auth_token|bearer)\s*[:=]\s*['\"]?[a-zA-Z0-9/+=\-_]{8,}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} \
  --exclude="*.{min.js,map,lock,log}" 2>/dev/null

# AWS Access Key pattern
grep -rInE "AKIA[0-9A-Z]{16}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# Google API Key pattern
grep -rInE "AIza[0-9A-Za-z\-_]{35}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# GitHub Token pattern
grep -rInE "gh[pousr]_[0-9a-zA-Z]{36,}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# Slack Token pattern
grep -rInE "xox[baprs]-[0-9a-zA-Z\-]{10,}" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# Generic high-entropy base64 strings
grep -rInE "['\"][a-zA-Z0-9+/=]{40,}['\"]" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} \
  --exclude="*.{min.js,map,lock,log,svg,jpg,png}" 2>/dev/null

# Private key detection
grep -rInE "BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# JWT Token detection
grep -rInE "eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# Database connection strings
grep -rInE "(mongodb(\+srv)?|mysql|postgresql|postgres):\/\/[^\s]*:[^\s]*@" . \
  --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null

# Environment files that shouldn't be committed
find . -type f \( -name ".env" -o -name ".env.*" -o -name "*.env" \) \
  -not -name ".env.example" -not -name ".env.template" 2>/dev/null
```

### Entropy-Based Detection

Use the bundled entropy detector for Shannon entropy analysis:

```bash
python3 scripts/entropy_detector.py "$REPOSITORY_PATH" --format json
```

Or run inline for environments without the script:

```python
import re, math

def calculate_entropy(string):
    if not string:
        return 0.0
    char_counts = {}
    for char in string:
        char_counts[char] = char_counts.get(char, 0) + 1
    entropy = 0.0
    for count in char_counts.values():
        probability = count / len(string)
        if probability > 0:
            entropy += -probability * math.log2(probability)
    return entropy
```

Thresholds:
- Minimum string length: 20 characters
- Minimum entropy: 4.5
- Confidence: >= 5.5 = High, >= 5.0 = Medium, < 5.0 = Low
- Context boost: if line contains password/secret/token/key/api/auth/credential

### Additional Tools (If Available)

```bash
git secrets --scan 2>/dev/null
pip-audit --format json 2>/dev/null || safety check --json 2>/dev/null
npm audit --json 2>/dev/null || yarn audit --json 2>/dev/null
govulncheck ./... 2>/dev/null
cargo audit --json 2>/dev/null
trivy fs --format json . 2>/dev/null
bandit -r . -f json 2>/dev/null
semgrep --config=auto --json 2>/dev/null
```

## Configuration Security Commands

```bash
# World-readable sensitive files
find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx" \
  -o -name ".env" -o -name "id_rsa" -o -name "id_dsa" \) -perm -004 2>/dev/null

# Group/world-writable config files
find . -type f \( -name "config.yml" -o -name "config.yaml" -o -name "config.json" \
  -o -name "*.conf" -o -name "settings.py" -o -name "application.properties" \) \
  -perm -022 2>/dev/null

# Executable config files (shouldn't be executable)
find . -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" \
  -o -name ".env*" \) -perm -111 2>/dev/null

# Sensitive files not in .gitignore
git ls-files --others --exclude-standard \
  | grep -E "\.(key|pem|p12|pfx|env)$|id_rsa|id_dsa" 2>/dev/null

# Unencrypted SSH private keys
find . -type f -name "id_*" -o -name "*.pem" | while read file; do
  if head -1 "$file" 2>/dev/null | grep -q "BEGIN.*PRIVATE KEY"; then
    if ! grep -q "ENCRYPTED" "$file"; then
      echo "$file: Unencrypted private key detected"
    fi
  fi
done

# World-writable directories
find . -type d -perm -002 ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null

# SUID/SGID files
find . -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null

# .git directory permissions
if [ -d .git ]; then
  ls -la .git | head -2
  find .git -type f -perm -044 2>/dev/null
fi
```

## Container Security Commands

```bash
# Find Dockerfiles
find . -type f \( -name "Dockerfile" -o -name "Dockerfile.*" -o -name "*.dockerfile" \) 2>/dev/null

# Root user usage
grep -rn "^USER root" . --include="Dockerfile*" 2>/dev/null

# Missing USER directive (defaults to root)
for dockerfile in $(find . -type f -name "Dockerfile*" 2>/dev/null); do
  if ! grep -q "^USER " "$dockerfile"; then
    echo "$dockerfile: No USER directive (runs as root)"
  fi
done

# Hardcoded secrets in Dockerfiles
grep -rInE "(ENV|ARG).*(PASSWORD|SECRET|KEY|TOKEN)\s*=" . --include="Dockerfile*" 2>/dev/null

# Latest tag usage (unpinned versions)
grep -rn "^FROM.*:latest" . --include="Dockerfile*" 2>/dev/null

# Missing base image version
grep -rn "^FROM [^:@]*$" . --include="Dockerfile*" 2>/dev/null

# ADD usage (COPY is preferred)
grep -rn "^ADD " . --include="Dockerfile*" 2>/dev/null

# Missing HEALTHCHECK
for dockerfile in $(find . -type f -name "Dockerfile*" 2>/dev/null); do
  if ! grep -q "^HEALTHCHECK" "$dockerfile"; then
    echo "$dockerfile: No HEALTHCHECK directive"
  fi
done

# apt-get without --no-install-recommends
grep -rn "apt-get install" . --include="Dockerfile*" \
  | grep -v "\-\-no-install-recommends" 2>/dev/null

# Exposed risky ports
grep -rn "^EXPOSE.*\(22\|23\|3389\|5432\|3306\|27017\|6379\)" . \
  --include="Dockerfile*" 2>/dev/null

# curl/wget without HTTPS
grep -rn "curl.*http:\|wget.*http:" . --include="Dockerfile*" 2>/dev/null

# Docker Compose security
if [ -f docker-compose.yml ] || [ -f docker-compose.yaml ]; then
  grep -n "privileged: true" docker-compose.y*ml 2>/dev/null
  grep -n "network_mode:.*host" docker-compose.y*ml 2>/dev/null
  grep -nE "volumes:.*(/etc|/var|/sys|/proc)" docker-compose.y*ml 2>/dev/null
  grep -nE "(password|secret|key|token):\s*['\"]?[a-zA-Z0-9]+" docker-compose.y*ml 2>/dev/null
fi

# Trivy image scanning (if available)
if command -v trivy &> /dev/null; then
  for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do
    trivy image --severity HIGH,CRITICAL --format json "$image" 2>/dev/null
  done
fi
```

## Dependency Discovery Commands

### Python

```bash
find . -type f \( -name "requirements.txt" -o -name "requirements-*.txt" \
  -o -name "Pipfile" -o -name "Pipfile.lock" -o -name "pyproject.toml" \
  -o -name "poetry.lock" -o -name "setup.py" -o -name "setup.cfg" \) 2>/dev/null

cat requirements.txt 2>/dev/null
grep -A 100 '^\[tool.poetry.dependencies\]' pyproject.toml 2>/dev/null || \
grep -A 100 '^\[project.dependencies\]' pyproject.toml 2>/dev/null
grep -A 50 "install_requires" setup.py 2>/dev/null
```

### JavaScript / Node.js

```bash
find . -type f -name "package.json" -not -path "*/node_modules/*" 2>/dev/null

cat package.json | grep -A 100 '"dependencies"' 2>/dev/null
cat package.json | grep -A 100 '"devDependencies"' 2>/dev/null

find . -type f \( -name "package-lock.json" -o -name "yarn.lock" \
  -o -name "pnpm-lock.yaml" \) -not -path "*/node_modules/*" 2>/dev/null
```

### Java / Maven

```bash
find . -type f -name "pom.xml" 2>/dev/null
grep -A 5 "<dependency>" pom.xml 2>/dev/null
mvn dependency:list -DoutputFile=dependencies.txt 2>/dev/null && cat dependencies.txt
```

### Java / Gradle

```bash
find . -type f \( -name "build.gradle" -o -name "build.gradle.kts" \) 2>/dev/null
grep -A 3 "dependencies {" build.gradle 2>/dev/null
gradle dependencies --configuration runtimeClasspath 2>/dev/null
```

### Ruby

```bash
find . -type f -name "Gemfile" 2>/dev/null
cat Gemfile 2>/dev/null
find . -type f -name "Gemfile.lock" 2>/dev/null
```

### Go

```bash
find . -type f -name "go.mod" 2>/dev/null
cat go.mod 2>/dev/null
go list -m all 2>/dev/null
```

### .NET

```bash
find . -type f \( -name "*.csproj" -o -name "*.vbproj" -o -name "packages.config" \) 2>/dev/null
grep "PackageReference" *.csproj 2>/dev/null
```

### Rust

```bash
find . -type f -name "Cargo.toml" 2>/dev/null
grep -A 100 '^\[dependencies\]' Cargo.toml 2>/dev/null
find . -type f -name "Cargo.lock" 2>/dev/null
```

### PHP

```bash
find . -type f -name "composer.json" 2>/dev/null
cat composer.json | grep -A 50 '"require"' 2>/dev/null
```

### Docker Base Images

```bash
find . -type f \( -name "Dockerfile" -o -name "Dockerfile.*" \) 2>/dev/null
grep -E "^FROM|^RUN.*install|^RUN.*apt-get|^RUN.*yum|^RUN.*apk" Dockerfile 2>/dev/null
```

## Code Security Patterns to Detect

| Category | What to Look For |
|----------|-----------------|
| SQL Injection | String concatenation in SQL queries, unsanitized user input |
| XSS | Unescaped user input in HTML templates, `innerHTML` usage |
| Command Injection | Unsanitized input in `os.system()`, `subprocess`, `exec` |
| Path Traversal | User input in file paths without sanitization |
| Insecure Crypto | MD5/SHA1 for passwords, hardcoded keys, weak algorithms |
| Insecure Deserialization | `pickle.loads()`, `yaml.load()` without SafeLoader |
| Missing Input Validation | Endpoints without input sanitization or type checking |

Map findings to:
- **CWE**: CWE-89 (SQLi), CWE-79 (XSS), CWE-78 (Command Injection), etc.
- **OWASP**: A01 (Access Control), A02 (Crypto), A03 (Injection), etc.

## OWASP Top 10 (2021) Reference

| ID | Category |
|----|----------|
| A01 | Broken Access Control |
| A02 | Cryptographic Failures |
| A03 | Injection |
| A04 | Insecure Design |
| A05 | Security Misconfiguration |
| A06 | Vulnerable and Outdated Components |
| A07 | Identification and Authentication Failures |
| A08 | Software and Data Integrity Failures |
| A09 | Security Logging and Monitoring Failures |
| A10 | Server-Side Request Forgery |
