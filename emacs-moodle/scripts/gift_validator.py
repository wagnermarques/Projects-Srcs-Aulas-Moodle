#!/usr/bin/env python3
"""
gift_validator.py - Syntax Validator for Moodle GIFT files
Author: Emacs Moodle Infrastructure
License: MIT
"""

import sys
import re
from pathlib import Path

def validate_gift(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        return False

    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()

    errors = 0
    warnings = 0
    in_question = False
    brace_count = 0
    question_start_line = 0

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Comment or blank line
        if stripped.startswith('//') or not stripped:
            continue

        # Check category line
        if stripped.startswith('$CATEGORY:'):
            continue

        # Check brace balance
        for char in line:
            if char == '{' and not line.startswith('//'):
                brace_count += 1
                if brace_count == 1:
                    in_question = True
                    question_start_line = idx
            elif char == '}' and not line.startswith('//'):
                brace_count -= 1
                if brace_count == 0:
                    in_question = False
                elif brace_count < 0:
                    print(f"[{path.name}:{idx}] ERROR: Unexpected closing brace '}}' without opening brace.")
                    errors += 1
                    brace_count = 0

        # Inside question answer block validation
        if in_question:
            # Check for invalid characters in answer block
            pass

    if brace_count > 0:
        print(f"[{path.name}:{question_start_line}] ERROR: Unclosed opening brace '{{' at end of file.")
        errors += 1

    if errors == 0:
        print(f"[✓] GIFT Validation passed for '{path.name}' (0 errors).")
        return True
    else:
        print(f"[✗] GIFT Validation failed for '{path.name}' ({errors} error(s) found).")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: gift_validator.py <file.gift> [<file2.gift> ...]")
        sys.exit(1)

    all_passed = True
    for gift_file in sys.argv[1:]:
        passed = validate_gift(gift_file)
        if not passed:
            all_passed = False

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
