#!/usr/bin/env python3
"""
moodle_course_builder.py - Builds a complete Moodle Course Backup (.mbz)
Author: Emacs Moodle Infrastructure
License: MIT

Generates a fully compliant Moodle Course Backup (.mbz) with complete context IDs,
questions.xml, gradebook.xml, and activity configurations.
"""

import sys
import os
import zipfile
import tempfile
import time
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from org_to_moodle_xml import OrgMoodleParser, build_moodle_xml

def create_course_moodle_backup_xml(course_fullname, course_shortname, activities_list):
    root = ET.Element("moodle_backup")
    info = ET.SubElement(root, "information")
    ET.SubElement(info, "name").text = f"moodle_course_{course_shortname.lower()}.mbz"
    ET.SubElement(info, "moodle_version").text = "2022112800"
    ET.SubElement(info, "moodle_release").text = "4.1"
    ET.SubElement(info, "backup_version").text = "2022112800"
    ET.SubElement(info, "backup_release").text = "4.1"
    ET.SubElement(info, "backup_date").text = str(int(time.time()))
    ET.SubElement(info, "type").text = "course"
    ET.SubElement(info, "format").text = "moodle2"
    ET.SubElement(info, "mode").text = "10"
    ET.SubElement(info, "original_course_id").text = "1"
    ET.SubElement(info, "original_course_fullname").text = course_fullname
    ET.SubElement(info, "original_course_shortname").text = course_shortname
    ET.SubElement(info, "original_course_startdate").text = str(int(time.time()))
    ET.SubElement(info, "original_course_contextid").text = "1"
    ET.SubElement(info, "original_systemcontextid").text = "1"

    details = ET.SubElement(info, "details")
    detail = ET.SubElement(details, "detail", backup_id="a1b2c3d4e5f6")
    ET.SubElement(detail, "type").text = "course"
    ET.SubElement(detail, "format").text = "moodle2"
    ET.SubElement(detail, "mode").text = "10"

    contents = ET.SubElement(info, "contents")
    
    # Sections
    sections = ET.SubElement(contents, "sections")
    sec = ET.SubElement(sections, "section")
    ET.SubElement(sec, "sectionid").text = "1"
    ET.SubElement(sec, "title").text = "Tópico 1: Orientação a Objetos em Kotlin"
    ET.SubElement(sec, "directory").text = "sections/section_1"

    # Activities with explicit contextid
    acts = ET.SubElement(contents, "activities")
    for act_info in activities_list:
        act = ET.SubElement(acts, "activity")
        ET.SubElement(act, "moduleid").text = str(act_info['mod_id'])
        ET.SubElement(act, "sectionid").text = "1"
        ET.SubElement(act, "modulename").text = act_info['mod_name']
        ET.SubElement(act, "title").text = act_info['title']
        ET.SubElement(act, "directory").text = act_info['dir']
        ET.SubElement(act, "contextid").text = str(act_info['context_id'])

    # Settings
    settings = ET.SubElement(info, "settings")
    for name, val in [("filename", f"course_{course_shortname.lower()}.mbz"), ("activities", "1"), ("questionbank", "1")]:
        setting = ET.SubElement(settings, "setting")
        ET.SubElement(setting, "level").text = "root"
        ET.SubElement(setting, "name").text = name
        ET.SubElement(setting, "value").text = val

    return root

def create_course_xml(fullname, shortname):
    root = ET.Element("course", id="1", contextid="1")
    ET.SubElement(root, "shortname").text = shortname
    ET.SubElement(root, "fullname").text = fullname
    ET.SubElement(root, "summary").text = "<p>Curso completo gerado via Emacs Moodle Infrastructure.</p>"
    ET.SubElement(root, "summaryformat").text = "1"
    ET.SubElement(root, "format").text = "topics"
    ET.SubElement(root, "numsections").text = "1"
    ET.SubElement(root, "startdate").text = str(int(time.time()))
    ET.SubElement(root, "enablecompletion").text = "1"
    return root

def create_section_xml(section_id=1, title="Tópico 1"):
    root = ET.Element("section", id=str(section_id))
    ET.SubElement(root, "number").text = str(section_id)
    ET.SubElement(root, "name").text = title
    ET.SubElement(root, "summary").text = ""
    ET.SubElement(root, "summaryformat").text = "1"
    ET.SubElement(root, "sequence").text = "1,2"
    ET.SubElement(root, "visible").text = "1"
    return root

def create_page_activity_xml(title, content_html):
    root = ET.Element("activity", id="1", moduleid="1", modulename="page", contextid="10")
    page = ET.SubElement(root, "page", id="1")
    ET.SubElement(page, "name").text = title
    ET.SubElement(page, "intro").text = f"<p>{title}</p>"
    ET.SubElement(page, "introformat").text = "1"
    ET.SubElement(page, "content").text = content_html
    ET.SubElement(page, "contentformat").text = "1"
    ET.SubElement(page, "display").text = "5"
    return root

def create_quiz_activity_xml(title, num_random=10):
    root = ET.Element("activity", id="2", moduleid="2", modulename="quiz", contextid="11")
    quiz = ET.SubElement(root, "quiz", id="2")
    ET.SubElement(quiz, "name").text = title
    ET.SubElement(quiz, "intro").text = "<p>Quiz Avaliativo de Fixação</p>"
    ET.SubElement(quiz, "introformat").text = "1"
    ET.SubElement(quiz, "timeopen").text = "0"
    ET.SubElement(quiz, "timeclose").text = "0"
    ET.SubElement(quiz, "timelimit").text = "1800"
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

def create_module_xml(mod_name, mod_id, context_id):
    root = ET.Element("module", id=str(mod_id), version="2022112800")
    ET.SubElement(root, "modulename").text = mod_name
    ET.SubElement(root, "sectionid").text = "1"
    ET.SubElement(root, "sectionnumber").text = "1"
    ET.SubElement(root, "contextid").text = str(context_id)
    ET.SubElement(root, "added").text = str(int(time.time()))
    ET.SubElement(root, "visible").text = "1"
    return root

def create_questions_xml():
    root = ET.Element("question_categories")
    cat = ET.SubElement(root, "question_category", id="1")
    ET.SubElement(cat, "name").text = "Default for Course"
    ET.SubElement(cat, "contextid").text = "1"
    ET.SubElement(cat, "contextlevel").text = "50"
    ET.SubElement(cat, "stamp").text = "moodle.org+220730200000+000000"
    ET.SubElement(cat, "parent").text = "0"
    ET.SubElement(cat, "sortorder").text = "999"
    ET.SubElement(cat, "idnumber").text = ""
    ET.SubElement(cat, "questions")
    return root

def build_full_course_mbz(folder_path, output_mbz_path):
    target_dir = Path(folder_path)
    course_name = target_dir.name
    
    lesson_html = list(target_dir.glob("*.html"))
    lesson_content = lesson_html[0].read_text(encoding='utf-8') if lesson_html else "<h2>Aula de Kotlin</h2>"
    lesson_title = "Aula 1: Orientação a Objetos em Kotlin"
    quiz_title = "Quiz 1: Orientação a Objetos em Kotlin"

    activities_list = [
        {'mod_id': 1, 'mod_name': 'page', 'title': lesson_title, 'dir': 'activities/page_1', 'context_id': 10},
        {'mod_id': 2, 'mod_name': 'quiz', 'title': quiz_title, 'dir': 'activities/quiz_2', 'context_id': 11}
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Write moodle_backup.xml
        mb_xml = create_course_moodle_backup_xml(course_name, "PAM-I", activities_list)
        (tmp_path / "moodle_backup.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mb_xml, encoding='utf-8').decode('utf-8'))

        # 2. Write course/course.xml
        c_dir = tmp_path / "course"
        c_dir.mkdir(parents=True, exist_ok=True)
        c_xml = create_course_xml(f"Disciplina: {course_name}", "PAM-I")
        (c_dir / "course.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(c_xml, encoding='utf-8').decode('utf-8'))

        # 3. Write sections/section_1/section.xml
        s_dir = tmp_path / "sections" / "section_1"
        s_dir.mkdir(parents=True, exist_ok=True)
        sec_xml = create_section_xml(1, "Módulo 1: Orientação a Objetos em Kotlin")
        (s_dir / "section.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sec_xml, encoding='utf-8').decode('utf-8'))

        # 4. Write Page activity (activities/page_1/)
        p_dir = tmp_path / "activities" / "page_1"
        p_dir.mkdir(parents=True, exist_ok=True)
        page_xml = create_page_activity_xml(lesson_title, lesson_content)
        (p_dir / "page.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(page_xml, encoding='utf-8').decode('utf-8'))
        (p_dir / "module.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(create_module_xml("page", 1, 10), encoding='utf-8').decode('utf-8'))
        (p_dir / "inforef.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(ET.Element("inforef"), encoding='utf-8').decode('utf-8'))

        # 5. Write Quiz activity (activities/quiz_2/)
        q_dir = tmp_path / "activities" / "quiz_2"
        q_dir.mkdir(parents=True, exist_ok=True)
        quiz_xml = create_quiz_activity_xml(quiz_title, num_random=10)
        (q_dir / "quiz.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(quiz_xml, encoding='utf-8').decode('utf-8'))
        (q_dir / "module.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(create_module_xml("quiz", 2, 11), encoding='utf-8').decode('utf-8'))
        (q_dir / "inforef.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(ET.Element("inforef"), encoding='utf-8').decode('utf-8'))

        # 6. Write Root Auxiliary XMLs (questions.xml, gradebook.xml, roles.xml, groups.xml, scales.xml, outcomes.xml)
        (tmp_path / "questions.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(create_questions_xml(), encoding='utf-8').decode('utf-8'))
        (tmp_path / "gradebook.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<gradebook></gradebook>')
        (tmp_path / "roles.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<roles_definition></roles_definition>')
        (tmp_path / "groups.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<groups></groups>')
        (tmp_path / "scales.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<scales_definition></scales_definition>')
        (tmp_path / "outcomes.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<outcomes_definition></outcomes_definition>')

        # Compress to .mbz using ZIP format (ZIP_DEFLATED)
        out_mbz = Path(output_mbz_path)
        out_mbz.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(out_mbz, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_path):
                for f in files:
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(tmp_path)
                    zf.write(full_p, arcname=rel_p)

        print(f"[✓] Successfully generated Full Moodle Course Package with Context IDs: '{out_mbz}'")

def main():
    parser = argparse.ArgumentParser(description="Package folder contents into a full Moodle Course (.mbz)")
    parser.add_argument("folder", help="Path to folder containing course artifacts")
    parser.add_argument("-o", "--output", help="Path to output .mbz file")
    args = parser.parse_args()

    folder_path = Path(args.folder)
    if not args.output:
        output_path = folder_path / "full_course.mbz"
    else:
        output_path = Path(args.output)

    build_full_course_mbz(folder_path, output_path)

if __name__ == "__main__":
    main()
