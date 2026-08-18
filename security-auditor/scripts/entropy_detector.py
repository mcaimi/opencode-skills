#!/usr/bin/env python3
"""
Entropy-based Secret Detector
Detects high-entropy strings that may be secrets using Shannon entropy calculation.

Usage:
    python3 entropy_detector.py [directory] [--min-length MIN] [--min-entropy ENTROPY] [--format FORMAT]

Arguments:
    directory       Directory to scan (default: current directory)
    --min-length    Minimum string length to analyze (default: 20)
    --min-entropy   Minimum entropy threshold (default: 4.5)
    --format        Output format: text, json, csv (default: text)
"""

import re
import math
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Set

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rb', '.php',
    '.yml', '.yaml', '.json', '.xml', '.conf', '.config', '.sh', '.bash',
    '.env', '.properties', '.ini', '.toml', '.rs', '.c', '.cpp', '.h',
    '.cs', '.swift', '.kt', '.scala', '.sql', '.tf', '.hcl'
}

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    '.git', 'node_modules', 'vendor', 'venv', '.venv', 'build', 'dist',
    'target', '__pycache__', '.pytest_cache', '.mypy_cache', '.tox',
    'coverage', '.coverage', 'htmlcov', 'wheels', 'eggs', '.eggs'
}

# File patterns to exclude
EXCLUDE_FILES = {
    '.min.js', '.map', '.lock', 'package-lock.json', 'yarn.lock',
    'Pipfile.lock', 'poetry.lock', 'Cargo.lock', 'Gemfile.lock'
}


def calculate_entropy(string: str) -> float:
    """
    Calculate Shannon entropy of a string.

    Args:
        string: Input string to analyze

    Returns:
        Entropy value (higher = more random/potentially a secret)
    """
    if not string:
        return 0.0

    # Count character frequencies
    char_counts = {}
    for char in string:
        char_counts[char] = char_counts.get(char, 0) + 1

    # Calculate entropy
    entropy = 0.0
    string_len = len(string)

    for count in char_counts.values():
        probability = count / string_len
        if probability > 0:
            entropy += -probability * math.log2(probability)

    return entropy


def is_likely_false_positive(string: str, file_path: str = '') -> bool:
    """
    Check if a high-entropy string is likely a false positive.
    """
    false_positive_patterns = [
        r'^[0-9a-f]{40}$',  # Git commit hashes
        r'^[A-Z_]+$',       # All caps constants
        r'^https?://',      # URLs
        r'^\d+\.\d+\.\d+',  # Version numbers
        r'^[A-F0-9]{32}$',  # MD5 hashes
        r'^[A-Za-z0-9+/]{40,}={0,2}$',  # Base64 data/test fixture
    ]

    for pattern in false_positive_patterns:
        if re.match(pattern, string):
            return True

    fp_path_segments = {'test', 'tests', 'mock', 'mocks', 'fixture', 'fixtures', '__tests__', '__mocks__'}
    if file_path:
        path_parts = set(Path(file_path).parts)
        if path_parts & fp_path_segments:
            return True

    if len(string) > 200:
        return True

    return False


def find_high_entropy_strings(
    file_path: Path,
    min_length: int = 20,
    min_entropy: float = 4.5
) -> List[Dict]:
    """
    Find strings with high entropy (potential secrets) in a file.

    Args:
        file_path: Path to file to scan
        min_length: Minimum string length to consider
        min_entropy: Minimum entropy threshold

    Returns:
        List of dictionaries containing findings
    """
    results = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip very long lines (likely minified code)
                if len(line) > 10000:
                    continue

                # Find potential secrets using various patterns
                patterns = [
                    # Quoted strings
                    r'["\']([a-zA-Z0-9+/=_\-]{20,})["\']',
                    # Variable assignments
                    r'[:=]\s*([a-zA-Z0-9+/=_\-]{20,})(?:\s|$|;|,)',
                    # Environment variables
                    r'export\s+\w+=["\']?([a-zA-Z0-9+/=_\-]{20,})["\']?',
                ]

                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        string = match.group(1)

                        # Apply length filter
                        if len(string) < min_length:
                            continue

                        # Calculate entropy
                        entropy = calculate_entropy(string)

                        # Apply entropy filter
                        if entropy < min_entropy:
                            continue

                        # Skip likely false positives
                        if is_likely_false_positive(string, str(file_path)):
                            continue

                        # Determine confidence based on entropy and context
                        confidence = 'Low'
                        if entropy >= 5.5:
                            confidence = 'High'
                        elif entropy >= 5.0:
                            confidence = 'Medium'

                        # Check for secret-related keywords in context
                        secret_keywords = ['password', 'secret', 'token', 'key', 'api', 'auth', 'credential']
                        if any(keyword in line.lower() for keyword in secret_keywords):
                            if confidence == 'Low':
                                confidence = 'Medium'
                            elif confidence == 'Medium':
                                confidence = 'High'

                        results.append({
                            'file': str(file_path),
                            'line': line_num,
                            'string': string[:60] + '...' if len(string) > 60 else string,
                            'entropy': round(entropy, 2),
                            'length': len(string),
                            'confidence': confidence,
                            'context': line.strip()[:100]
                        })

    except (UnicodeDecodeError, PermissionError, FileNotFoundError) as e:
        # Skip files that can't be read
        pass

    return results


def scan_directory(
    directory: Path,
    min_length: int = 20,
    min_entropy: float = 4.5,
    extensions: Set[str] = None
) -> List[Dict]:
    """
    Recursively scan directory for high-entropy strings.

    Args:
        directory: Directory to scan
        min_length: Minimum string length
        min_entropy: Minimum entropy threshold
        extensions: Set of file extensions to scan (default: SCANNABLE_EXTENSIONS)

    Returns:
        List of all findings
    """
    if extensions is None:
        extensions = SCANNABLE_EXTENSIONS

    all_results = []

    for path in directory.rglob('*'):
        # Skip if not a file
        if not path.is_file():
            continue

        # Skip if extension not in whitelist
        if path.suffix not in extensions and path.name not in {'.env', '.env.local', '.env.production'}:
            continue

        # Skip if in excluded directory
        if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
            continue

        # Skip if excluded file pattern
        if any(path.name.endswith(pattern) for pattern in EXCLUDE_FILES):
            continue

        # Scan the file
        results = find_high_entropy_strings(path, min_length, min_entropy)
        all_results.extend(results)

    return all_results


def format_output(results: List[Dict], format_type: str = 'text') -> str:
    """
    Format results for output.

    Args:
        results: List of findings
        format_type: Output format (text, json, csv)

    Returns:
        Formatted output string
    """
    if format_type == 'json':
        return json.dumps(results, indent=2)

    elif format_type == 'csv':
        lines = ['File,Line,Entropy,Length,Confidence,String']
        for r in results:
            escaped = r['string'].replace('"', '""')
            lines.append(f"{r['file']},{r['line']},{r['entropy']},{r['length']},{r['confidence']},\"{escaped}\"")
        return '\n'.join(lines)

    else:  # text format
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"High-Entropy String Detection Results")
        output.append(f"{'='*80}\n")
        output.append(f"Total potential secrets found: {len(results)}\n")

        # Group by confidence
        by_confidence = {'High': [], 'Medium': [], 'Low': []}
        for r in results:
            by_confidence[r['confidence']].append(r)

        for confidence in ['High', 'Medium', 'Low']:
            items = by_confidence[confidence]
            if not items:
                continue

            output.append(f"\n{confidence} Confidence ({len(items)} findings)")
            output.append("-" * 80)

            # Sort by entropy (descending)
            for r in sorted(items, key=lambda x: x['entropy'], reverse=True):
                output.append(f"\n📍 {r['file']}:{r['line']}")
                output.append(f"   Entropy: {r['entropy']} | Length: {r['length']} | Confidence: {r['confidence']}")
                output.append(f"   String: {r['string']}")
                output.append(f"   Context: {r['context']}")

        output.append(f"\n{'='*80}\n")
        return '\n'.join(output)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detect high-entropy strings that may be secrets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )

    parser.add_argument(
        '--min-length',
        type=int,
        default=20,
        help='Minimum string length to analyze (default: 20)'
    )

    parser.add_argument(
        '--min-entropy',
        type=float,
        default=4.5,
        help='Minimum entropy threshold (default: 4.5)'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Scan directory
    results = scan_directory(
        directory,
        min_length=args.min_length,
        min_entropy=args.min_entropy
    )

    # Output results
    output = format_output(results, args.format)
    print(output)

    # Exit with appropriate code
    sys.exit(0 if len(results) == 0 else 1)


if __name__ == '__main__':
    main()
