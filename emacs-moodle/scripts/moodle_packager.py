#!/usr/bin/env python3
"""
moodle_packager.py - Generates standalone Moodle MBZ backup packages from Org files
Author: Emacs Moodle Infrastructure
License: MIT
"""

import sys
import os
import zipfile
import tempfile
import time
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

def create_moodle_backup_xml(quiz_title, mod_id=1, context_id=10):
    root = ET.Element("moodle_backup")
    info = ET.SubElement(root, "information")
    ET.SubElement(info, "name").text = "moodle_quiz_activity.mbz"
    ET.SubElement(info, "moodle_version").text = "2022112800"
    ET.SubElement(info, "moodle_release").text = "4.1"
    ET.SubElement(info, "backup_version").text = "2022112800"
    ET.SubElement(info, "backup_release").text = "4.1"
    ET.SubElement(info, "backup_date").text = str(int(time.time()))
    ET.SubElement(info, "type").text = "activity"
    ET.SubElement(info, "format").text = "moodle2"
    ET.SubElement(info, "mode").text = "10"
    ET.SubElement(info, "original_course_id").text = "1"
    ET.SubElement(info, "original_systemcontextid").text = "1"

    details = ET.SubElement(info, "details")
    detail = ET.SubElement(details, "detail", backup_id="a1b2c3d4e5f6")
    ET.SubElement(detail, "type").text = "activity"
    ET.SubElement(detail, "format").text = "moodle2"
    ET.SubElement(detail, "mode").text = "10"

    contents = ET.SubElement(info, "contents")
    activities = ET.SubElement(contents, "activities")
    act = ET.SubElement(activities, "activity")
    ET.SubElement(act, "moduleid").text = str(mod_id)
    ET.SubElement(act, "sectionid").text = "1"
    ET.SubElement(act, "modulename").text = "quiz"
    ET.SubElement(act, "title").text = quiz_title
    ET.SubElement(act, "directory").text = f"activities/quiz_{mod_id}"
    ET.SubElement(act, "contextid").text = str(context_id)

    settings = ET.SubElement(info, "settings")
    for name, val in [("filename", "moodle_quiz_activity.mbz"), ("activities", "1"), ("questionbank", "1")]:
        setting = ET.SubElement(settings, "setting")
        ET.SubElement(setting, "level").text = "root"
        ET.SubElement(setting, "name").text = name
        ET.SubElement(setting, "value").text = val

    return root

def create_quiz_activity_xml(quiz_title, num_random=10, time_limit=0):
    root = ET.Element("activity", id="1", moduleid="1", modulename="quiz", contextid="10")
    quiz = ET.SubElement(root, "quiz", id="1")
    ET.SubElement(quiz, "name").text = quiz_title
    ET.SubElement(quiz, "intro").text = "<p>Auto-generated Quiz Activity from Emacs Org-mode.</p>"
    ET.SubElement(quiz, "introformat").text = "1"
    ET.SubElement(quiz, "timeopen").text = "0"
    ET.SubElement(quiz, "timeclose").text = "0"
    ET.SubElement(quiz, "timelimit").text = str(time_limit * 60)
    ET.SubElement(quiz, "attempts").text = "0"
    ET.SubElement(quiz, "sumgrades").text = str(float(num_random))
    ET.SubElement(quiz, "grade").text = "10.0"

    slots = ET.SubElement(quiz, "slots")
    for idx in range(1, num_random + 1):
        slot = ET.SubElement(slots, "slot", id=str(idx))
        ET.SubElement(slot, "slot").text = str(idx)
        ET.SubElement(slot, "page").text = str(idx)
        ET.SubElement(slot, "maxmark").text = "1.0000000"

    return root

def create_module_xml(quiz_title, context_id=10):
    root = ET.Element("module", id="1", version="2022112800")
    ET.SubElement(root, "modulename").text = "quiz"
    ET.SubElement(root, "sectionid").text = "1"
    ET.SubElement(root, "sectionnumber").text = "1"
    ET.SubElement(root, "contextid").text = str(context_id)
    ET.SubElement(root, "added").text = str(int(time.time()))
    ET.SubElement(root, "visible").text = "1"
    return root

def package_org_to_mbz(org_file_path, output_mbz_path):
    input_path = Path(org_file_path)
    quiz_title = input_path.stem.replace('_', ' ').title()
    num_random = 10

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Write moodle_backup.xml
        mb_xml = create_moodle_backup_xml(quiz_title)
        (tmp_path / "moodle_backup.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mb_xml, encoding='utf-8').decode('utf-8'))

        # Write activities/quiz_1/
        act_dir = tmp_path / "activities" / "quiz_1"
        act_dir.mkdir(parents=True, exist_ok=True)

        quiz_xml = create_quiz_activity_xml(quiz_title, num_random=num_random)
        (act_dir / "quiz.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(quiz_xml, encoding='utf-8').decode('utf-8'))

        mod_xml = create_module_xml(quiz_title, context_id=10)
        (act_dir / "module.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mod_xml, encoding='utf-8').decode('utf-8'))

        inforef_xml = ET.Element("inforef")
        (act_dir / "inforef.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(inforef_xml, encoding='utf-8').decode('utf-8'))

        # Write Root Auxiliary XMLs (questions.xml, gradebook.xml, etc.)
        q_root = ET.Element("question_categories")
        cat = ET.SubElement(q_root, "question_category", id="1")
        ET.SubElement(cat, "name").text = "Default"
        ET.SubElement(cat, "contextid").text = "1"
        ET.SubElement(cat, "contextlevel").text = "50"
        (tmp_path / "questions.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(q_root, encoding='utf-8').decode('utf-8'))

        # Compress to .mbz using ZIP format (ZIP_DEFLATED)
        out_mbz = Path(output_mbz_path)
        out_mbz.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(out_mbz, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_path):
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(tmp_path)
                    zf.write(full_p, arcname=rel_p)

        print(f"[✓] Successfully generated Moodle MBZ Package with Context IDs: '{out_mbz}'")

def main():
    parser = argparse.ArgumentParser(description="Package Org file into Moodle Activity Restore (.mbz)")
    parser.add_argument("input", help="Path to input .org quiz file")
    parser.add_argument("-o", "--output", help="Path to output .mbz file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not args.output:
        output_path = input_path.with_suffix('.mbz')
    else:
        output_path = Path(args.output)

    package_org_to_mbz(input_path, output_path)

if __name__ == "__main__":
    main()
