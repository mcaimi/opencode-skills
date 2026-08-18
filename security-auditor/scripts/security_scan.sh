#!/bin/bash
#
# Security Scanner - Comprehensive security audit script
# Implements the detection commands from the Security Auditor Agent
#
# Usage: ./security_scan.sh [directory] [--quick|--full|--secrets-only|--config-only|--docker-only]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SCAN_DIR="${1:-.}"
SCAN_MODE="${2:---full}"

# Counters
TOTAL_ISSUES=0
CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0
LOW_ISSUES=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${GREEN}--- $1 ---${NC}"
    echo ""
}

print_critical() {
    echo -e "${RED}[CRITICAL] $1${NC}"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

print_high() {
    echo -e "${RED}[HIGH] $1${NC}"
    HIGH_ISSUES=$((HIGH_ISSUES + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

print_medium() {
    echo -e "${YELLOW}[MEDIUM] $1${NC}"
    MEDIUM_ISSUES=$((MEDIUM_ISSUES + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

print_low() {
    echo -e "[LOW] $1"
    LOW_ISSUES=$((LOW_ISSUES + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
}

print_ok() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Handle help before anything else
if [ "$SCAN_MODE" = "-h" ] || [ "$SCAN_MODE" = "--help" ]; then
    echo "Usage: $0 [directory] [--quick|--full|--secrets-only|--config-only|--docker-only]"
    exit 0
fi

# Change to scan directory
cd "$SCAN_DIR" || exit 1

print_header "Security Audit Report"
echo "Directory: $(pwd)"
echo "Scan Mode: $SCAN_MODE"
echo "Date: $(date)"

# Function: Scan for secrets
scan_secrets() {
    print_section "Credential & Secret Detection"

    # AWS Access Keys
    echo "Scanning for AWS Access Keys..."
    aws_keys=$(grep -rInE "AKIA[0-9A-Z]{16}" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$aws_keys" ]; then
        print_critical "AWS Access Keys detected:"
        echo "$aws_keys" | head -10
        aws_key_count=$(echo "$aws_keys" | wc -l | tr -d ' ')
        [ "$aws_key_count" -gt 10 ] && echo "... and $((aws_key_count - 10)) more"
    else
        print_ok "No AWS Access Keys detected"
    fi

    # Google API Keys
    echo "Scanning for Google API Keys..."
    google_keys=$(grep -rInE "AIza[0-9A-Za-z\-_]{35}" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$google_keys" ]; then
        print_critical "Google API Keys detected:"
        echo "$google_keys" | head -10
    else
        print_ok "No Google API Keys detected"
    fi

    # GitHub Tokens
    echo "Scanning for GitHub Tokens..."
    github_tokens=$(grep -rInE "gh[pousr]_[0-9a-zA-Z]{36,}" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$github_tokens" ]; then
        print_critical "GitHub Tokens detected:"
        echo "$github_tokens" | head -10
    else
        print_ok "No GitHub Tokens detected"
    fi

    # Slack Tokens
    echo "Scanning for Slack Tokens..."
    slack_tokens=$(grep -rInE "xox[baprs]-[0-9a-zA-Z\-]{10,}" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$slack_tokens" ]; then
        print_critical "Slack Tokens detected:"
        echo "$slack_tokens" | head -10
    else
        print_ok "No Slack Tokens detected"
    fi

    # Private Keys
    echo "Scanning for Private Keys..."
    private_keys=$(grep -rInE "BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$private_keys" ]; then
        print_critical "Private Keys detected:"
        echo "$private_keys" | head -10
    else
        print_ok "No Private Keys detected"
    fi

    # JWT Tokens
    echo "Scanning for JWT Tokens..."
    jwt_tokens=$(grep -rInE "eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$jwt_tokens" ]; then
        print_high "JWT Tokens detected:"
        echo "$jwt_tokens" | head -10
    else
        print_ok "No JWT Tokens detected"
    fi

    # Database Connection Strings
    echo "Scanning for Database Connection Strings..."
    db_strings=$(grep -rInE "(mongodb(\+srv)?|mysql|postgresql|postgres):\/\/[^\s]*:[^\s]*@" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} 2>/dev/null || true)
    if [ -n "$db_strings" ]; then
        print_high "Database Connection Strings with credentials detected:"
        echo "$db_strings" | head -10
    else
        print_ok "No Database Connection Strings with credentials detected"
    fi

    # Generic high-entropy strings
    echo "Scanning for generic secrets..."
    generic_secrets=$(grep -rInE "(password|passwd|pwd|secret|token|api_key|apikey|api-key|access_key|secret_key|private_key|client_secret|auth_token|bearer)\s*[:=]\s*['\"]?[a-zA-Z0-9/+=\-_]{12,}" . \
        --exclude-dir={.git,node_modules,vendor,venv,.venv,build,dist,target} \
        --exclude="*.min.js" --exclude="*.map" --exclude="*.lock" --exclude="*.log" 2>/dev/null | head -10 || true)
    if [ -n "$generic_secrets" ]; then
        print_high "Generic secret patterns detected:"
        echo "$generic_secrets"
    else
        print_ok "No generic secret patterns detected"
    fi

    # .env files
    echo "Checking for committed .env files..."
    env_files=$(find . -type f \( -name ".env" -o -name ".env.local" -o -name ".env.production" \) \
        -not -name ".env.example" -not -name ".env.template" 2>/dev/null || true)
    if [ -n "$env_files" ]; then
        print_critical "Environment files committed to repository:"
        echo "$env_files"
    else
        print_ok "No .env files committed"
    fi

    # Entropy-based detection (if Python available)
    if command -v python3 &> /dev/null; then
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -f "$script_dir/entropy_detector.py" ]; then
            echo "Running entropy-based secret detection..."
            entropy_results=$(python3 "$script_dir/entropy_detector.py" . --format json 2>/dev/null || echo "[]")
            entropy_count=$(echo "$entropy_results" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

            if [ "$entropy_count" -gt 0 ]; then
                print_high "High-entropy strings detected: $entropy_count potential secrets"
                echo "Run 'python3 $script_dir/entropy_detector.py' for details"
            else
                print_ok "No high-entropy strings detected"
            fi
        fi
    fi
}

# Function: Scan configuration security
scan_config() {
    print_section "Configuration Security"

    # World-readable sensitive files
    echo "Checking for world-readable sensitive files..."
    world_readable=$(find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx" -o -name ".env" -o -name "id_rsa" \) \
        -perm -004 2>/dev/null || true)
    if [ -n "$world_readable" ]; then
        print_high "World-readable sensitive files detected:"
        echo "$world_readable"
    else
        print_ok "No world-readable sensitive files"
    fi

    # Group/world-writable configs
    echo "Checking for writable config files..."
    writable_configs=$(find . -type f \( -name "config.yml" -o -name "config.yaml" -o -name "*.conf" -o -name "settings.py" \) \
        -perm -022 2>/dev/null || true)
    if [ -n "$writable_configs" ]; then
        print_medium "Group/world-writable config files detected:"
        echo "$writable_configs"
    else
        print_ok "No overly permissive config files"
    fi

    # Executable config files
    echo "Checking for executable config files..."
    executable_configs=$(find . -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name ".env*" \) \
        -perm -111 2>/dev/null || true)
    if [ -n "$executable_configs" ]; then
        print_medium "Executable config files detected (shouldn't be executable):"
        echo "$executable_configs"
    else
        print_ok "No executable config files"
    fi

    # SUID/SGID files
    echo "Checking for SUID/SGID files..."
    suid_files=$(find . -type f \( -perm -4000 -o -perm -2000 \) 2>/dev/null || true)
    if [ -n "$suid_files" ]; then
        print_high "SUID/SGID files detected:"
        echo "$suid_files"
    else
        print_ok "No SUID/SGID files"
    fi
}

# Function: Scan Docker security
scan_docker() {
    print_section "Container Security (Docker)"

    local -a dockerfiles=()
    while IFS= read -r -d '' f; do
        dockerfiles+=("$f")
    done < <(find . -type f \( -name "Dockerfile" -o -name "Dockerfile.*" \) -print0 2>/dev/null)

    if [ ${#dockerfiles[@]} -eq 0 ]; then
        echo "No Dockerfiles found"
        return
    fi

    echo "Found ${#dockerfiles[@]} Dockerfile(s)"

    # Latest tag usage
    echo "Checking for :latest tag usage..."
    latest_tags=$(grep -rn "^FROM.*:latest" . --include="Dockerfile*" 2>/dev/null || true)
    if [ -n "$latest_tags" ]; then
        print_medium "Dockerfiles using :latest tag (should pin versions):"
        echo "$latest_tags"
    else
        print_ok "No :latest tags found"
    fi

    # Running as root
    echo "Checking for root user..."
    for dockerfile in "${dockerfiles[@]}"; do
        if ! grep -q "^USER " "$dockerfile"; then
            print_high "No USER directive in $dockerfile (will run as root)"
        fi
    done

    # Hardcoded secrets
    echo "Checking for hardcoded secrets in Dockerfiles..."
    docker_secrets=$(grep -rInE "(ENV|ARG).*(PASSWORD|SECRET|KEY|TOKEN)\s*=" . --include="Dockerfile*" 2>/dev/null || true)
    if [ -n "$docker_secrets" ]; then
        print_critical "Hardcoded secrets in Dockerfiles:"
        echo "$docker_secrets"
    else
        print_ok "No hardcoded secrets in Dockerfiles"
    fi

    # Missing HEALTHCHECK
    echo "Checking for HEALTHCHECK directives..."
    for dockerfile in "${dockerfiles[@]}"; do
        if ! grep -q "^HEALTHCHECK" "$dockerfile"; then
            print_low "No HEALTHCHECK in $dockerfile"
        fi
    done

    # ADD vs COPY
    echo "Checking for ADD usage (COPY is preferred)..."
    add_usage=$(grep -rn "^ADD " . --include="Dockerfile*" 2>/dev/null || true)
    if [ -n "$add_usage" ]; then
        print_low "ADD command usage (prefer COPY):"
        echo "$add_usage"
    fi

    # Docker Compose security
    if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
        echo "Checking docker-compose.yml security..."

        privileged=$(grep -n "privileged: true" docker-compose.y*ml 2>/dev/null || true)
        if [ -n "$privileged" ]; then
            print_high "Privileged mode in docker-compose.yml:"
            echo "$privileged"
        fi

        host_network=$(grep -n "network_mode:.*host" docker-compose.y*ml 2>/dev/null || true)
        if [ -n "$host_network" ]; then
            print_medium "Host network mode in docker-compose.yml:"
            echo "$host_network"
        fi
    fi
}

# Function: Generate summary
generate_summary() {
    print_header "Audit Summary"

    echo "Total Issues Found: $TOTAL_ISSUES"
    echo ""
    echo -e "${RED}Critical: $CRITICAL_ISSUES${NC}"
    echo -e "${RED}High:     $HIGH_ISSUES${NC}"
    echo -e "${YELLOW}Medium:   $MEDIUM_ISSUES${NC}"
    echo "Low:      $LOW_ISSUES"
    echo ""

    # Calculate score
    SCORE=$((100 - (CRITICAL_ISSUES * 40) - (HIGH_ISSUES * 20) - (MEDIUM_ISSUES * 10) - (LOW_ISSUES * 5)))
    [ $SCORE -lt 0 ] && SCORE=0

    if [ $SCORE -ge 90 ]; then
        GRADE="A"
        STATUS="${GREEN}Excellent${NC}"
    elif [ $SCORE -ge 80 ]; then
        GRADE="B"
        STATUS="${GREEN}Good${NC}"
    elif [ $SCORE -ge 70 ]; then
        GRADE="C"
        STATUS="${YELLOW}Fair${NC}"
    elif [ $SCORE -ge 60 ]; then
        GRADE="D"
        STATUS="${RED}Poor${NC}"
    else
        GRADE="F"
        STATUS="${RED}Critical${NC}"
    fi

    echo -e "Security Score: $SCORE/100 (Grade: $GRADE)"
    echo -e "Security Posture: $STATUS"
    echo ""

    if [ $CRITICAL_ISSUES -gt 0 ]; then
        echo -e "${RED}⚠️  CRITICAL: Immediate action required!${NC}"
    elif [ $HIGH_ISSUES -gt 0 ]; then
        echo -e "${RED}⚠️  HIGH: Prompt remediation recommended${NC}"
    elif [ $MEDIUM_ISSUES -gt 0 ]; then
        echo -e "${YELLOW}⚠️  MEDIUM: Address these issues in the near term${NC}"
    else
        echo -e "${GREEN}✓ No critical or high severity issues found${NC}"
    fi

    # Exit code
    if [ $CRITICAL_ISSUES -gt 0 ]; then
        exit 2
    elif [ $HIGH_ISSUES -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Main execution
case $SCAN_MODE in
    --secrets-only)
        scan_secrets
        ;;
    --config-only)
        scan_config
        ;;
    --docker-only)
        scan_docker
        ;;
    --quick)
        scan_secrets
        scan_config
        ;;
    --full|*)
        scan_secrets
        scan_config
        scan_docker
        ;;
esac

generate_summary
