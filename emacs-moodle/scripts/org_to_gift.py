#!/usr/bin/env python3
"""
org_to_gift.py - Converts Org-mode quiz files to Moodle GIFT format
Author: Emacs Moodle Infrastructure
License: MIT
"""

import sys
import re
from pathlib import Path
from org_to_moodle_xml import OrgMoodleParser

def question_to_gift(q):
    """Converts a parsed question dictionary into GIFT format syntax."""
    output = []
    
    # Category tag if present
    cat = q.get('category', '').replace('$course$/', '')
    if cat:
        output.append(f"$CATEGORY: {cat}\n")

    title = q['title'].replace(':', r'\:')
    qtype = q['type']
    body = q['body'].strip()
    
    if body and body != title:
        qtext = f"::{title}:: {body}"
    else:
        qtext = f"::{title}::"

    if qtype == 'multichoice':
        answers = []
        for opt in q['options']:
            prefix = "=" if opt['is_correct'] else "~"
            fb = f" #{opt['feedback']}" if opt['feedback'] else ""
            answers.append(f"  {prefix}{opt['text']}{fb}")
        ans_block = " {\n" + "\n".join(answers) + "\n}"
        output.append(f"{qtext}{ans_block}\n")

    elif qtype == 'truefalse':
        correct_opt = next((opt for opt in q['options'] if opt['is_correct']), None)
        ans_val = "TRUE" if (correct_opt and correct_opt['text'].lower() in ['true', 'v', 'verdadeiro', 'yes']) else "FALSE"
        output.append(f"{qtext} {{{ans_val}}}\n")

    elif qtype == 'shortanswer':
        answers = []
        for opt in q['options']:
            fb = f" #{opt['feedback']}" if opt['feedback'] else ""
            answers.append(f"  ={opt['text']}{fb}")
        ans_block = " {\n" + "\n".join(answers) + "\n}"
        output.append(f"{qtext}{ans_block}\n")

    elif qtype == 'matching':
        answers = []
        for opt in q['options']:
            answers.append(f"  ={opt['text']} -> {opt['feedback']}")
        ans_block = " {\n" + "\n".join(answers) + "\n}"
        output.append(f"{qtext}{ans_block}\n")

    elif qtype == 'numerical':
        answers = []
        tol = q['properties'].get('TOLERANCE', '0')
        for opt in q['options']:
            fb = f" #{opt['feedback']}" if opt['feedback'] else ""
            answers.append(f"  =#{opt['text']}:{tol}{fb}")
        ans_block = " {\n" + "\n".join(answers) + "\n}"
        output.append(f"{qtext}{ans_block}\n")

    elif qtype == 'essay':
        output.append(f"{qtext} {{}}\n")

    return "\n".join(output)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert Org-mode quiz files to Moodle GIFT format.")
    parser.add_argument("input", help="Path to input .org file")
    parser.add_argument("-o", "--output", help="Path to output .gift file")
    parser.add_argument("-r", "--random", type=int, help="Randomly sample N questions from question bank")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.gift')

    org_parser = OrgMoodleParser(input_path)
    questions = org_parser.parse()

    if args.random and args.random > 0:
        import random
        if len(questions) > args.random:
            print(f"[*] Randomly sampling {args.random} question(s) out of {len(questions)}...")
            questions = random.sample(questions, args.random)

    gift_blocks = []
    for q in questions:
        gift_blocks.append(question_to_gift(q))

    gift_content = "\n\n".join(gift_blocks)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(gift_content, encoding='utf-8')
    print(f"[✓] Successfully exported GIFT to '{output_path}' ({len(questions)} question(s)).")

if __name__ == "__main__":
    main()
