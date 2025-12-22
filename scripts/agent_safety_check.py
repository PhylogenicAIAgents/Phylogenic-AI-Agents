#!/usr/bin/env python3
"""Basic agent safety check script (placeholder).

Scans repository for potential secret-like strings and flags files under AGENTS/ or src/agent modules.
"""
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"(?i)api[_-]?key"),
    re.compile(r"(?i)secret"),
    re.compile(r"(?i)aws[_-]?secret"),
    re.compile(r"(?i)password"),
]

ROOT = Path(__file__).resolve().parents[1]

def scan_file(path: Path):
    text = path.read_text(errors='ignore')
    matches = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            # Heuristic: only flag if there is a likely secret value nearby
            # Look for quoted strings of length >= 16 or known prefixes
            # More precise heuristic: look for assignments of long quoted strings
            # Only consider long continuous token-like strings (no whitespace)
            assignment_pattern = re.compile(
                r"[A-Za-z_][A-Za-z0-9_]*\s*=\s*['\"][A-Za-z0-9_\-\+/=]{16,}['\"]"
            )
            environ_default_pattern = re.compile(
                r"os\.environ\.get\(\s*['\"][A-Za-z0-9_]+['\"]\s*,\s*['\"][A-Za-z0-9_\-\+/=]{16,}['\"]\s*\)"
            )
            if assignment_pattern.search(text) or environ_default_pattern.search(text):
                matches.append(pattern.pattern)
    return matches


def main():
    flagged = []
    # Focus scan on source code and agent specs to reduce false positives
    scan_paths = [ROOT / 'src', ROOT / 'AGENTS']
    for base in scan_paths:
        if not base.exists():
            continue
        for p in base.rglob("*.*"):
            if p.suffix in {'.py', '.env', '.cfg', '.yaml', '.yml', '.md'}:
                matches = scan_file(p)
                if matches:
                    flagged.append((p.relative_to(ROOT), matches))

    if flagged:
        print("Potential secret-like patterns found in files:")
        for f, m in flagged:
            print(f" - {f}: {', '.join(m)}")
        print("\nPlease ensure secrets are stored in GitHub secrets and not in the repository.")
        sys.exit(2)

    print("No obvious secret patterns found.")

if __name__ == '__main__':
    main()
