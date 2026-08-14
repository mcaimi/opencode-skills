# Scripts

Executable tools bundled with the security-auditor skill.

## entropy_detector.py

Shannon entropy-based secret detector. No external dependencies (Python 3.7+
standard library only).

```bash
python3 scripts/entropy_detector.py [directory] [--min-length N] [--min-entropy N] [--format text|json|csv]
```

Exit codes: `0` = no findings, `1` = potential secrets detected.

## security_scan.sh

Comprehensive security scanner covering credentials, configuration, and
container security.

```bash
bash scripts/security_scan.sh [directory] [--full|--quick|--secrets-only|--config-only|--docker-only]
```

Exit codes: `0` = no critical/high issues, `1` = high severity, `2` = critical.

## CI/CD Integration

```bash
if ! python3 scripts/entropy_detector.py --min-entropy 5.0; then
    echo "Potential secrets detected!"
    exit 1
fi
```
