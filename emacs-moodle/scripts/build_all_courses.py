#!/usr/bin/env python3
"""
build_all_courses.py - Automated Batch Builder for Moodle Course Packages (.mbz)
Author: Emacs Moodle Infrastructure
License: MIT

Scans directories for .org lessons and quizzes, compiles all HTML/XML/GIFT artifacts,
and automatically builds complete Moodle Course Packages (.mbz) for 1-click Moodle restore.
"""

import sys
import os
import subprocess
from pathlib import Path
from moodle_course_builder import build_full_course_mbz
from org_to_moodle_xml import OrgMoodleParser, build_moodle_xml, prettify_xml
from org_to_gift import question_to_gift

def compile_org_files_in_folder(folder_path):
    target_dir = Path(folder_path)
    org_files = list(target_dir.glob("*.org"))
    if not org_files:
        return False

    print(f"[*] Processing directory: '{target_dir}' ({len(org_files)} .org file(s) found)...")

    for org_file in org_files:
        content = org_file.read_text(encoding='utf-8')
        
        # Check if it's a Quiz Bank or Lesson
        if ":TYPE:" in content or "Category:" in content or "[MCQ]" in content or "[TF]" in content:
            # Build XML
            xml_file = org_file.with_suffix('.xml')
            parser = OrgMoodleParser(org_file)
            questions = parser.parse()
            xml_tree = build_moodle_xml(questions)
            pretty_xml = prettify_xml(xml_tree)
            xml_file.write_text(pretty_xml, encoding='utf-8')

            # Build GIFT
            gift_file = org_file.with_suffix('.gift')
            gift_blocks = [question_to_gift(q) for q in questions]
            gift_file.write_text("\n\n".join(gift_blocks), encoding='utf-8')
            print(f"  [✓] Compiled Quiz: '{org_file.name}' -> XML & GIFT")

        else:
            # Export Lesson HTML using Emacs batch mode
            html_file = org_file.with_suffix('.html')
            cmd = [
                "emacs", str(org_file), "--batch",
                "--eval", "(progn (require 'ox-html) (org-html-export-to-html))"
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  [✓] Compiled Lesson: '{org_file.name}' -> HTML")

    # Build Full Course .mbz Package inside the folder
    course_mbz = target_dir / f"curso_{target_dir.name.replace(' ', '_')}.mbz"
    build_full_course_mbz(target_dir, course_mbz)
    return True

def main():
    root_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("2026Sem2-AuxDomiciliar/lcd")
    
    if not root_dir.exists():
        print(f"Error: Path '{root_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"==================================================")
    print(f"  Automated Moodle Course Batch Builder")
    print(f"  Target Root: {root_dir}")
    print(f"==================================================")

    # Check if root_dir itself has .org files or subdirectories
    subdirs = [d for d in root_dir.iterdir() if d.is_dir()]
    if not subdirs:
        compile_org_files_in_folder(root_dir)
    else:
        processed_count = 0
        for subdir in subdirs:
            if compile_org_files_in_folder(subdir):
                processed_count += 1

        print(f"\n[✓] Successfully processed {processed_count} course directory/directories!")

if __name__ == "__main__":
    main()
