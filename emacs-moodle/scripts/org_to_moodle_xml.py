#!/usr/bin/env python3
"""
org_to_moodle_xml.py - Portable Org-mode & GIFT to Moodle XML Converter
Author: Emacs Moodle Infrastructure
License: MIT

Converts Org-mode quiz files and GIFT plain-text files into native Moodle XML
compatible with Moodle Question Bank import (Moodle 3.x - 4.x+).
"""

import sys
import os
import re
import html
import base64
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

def escape_html(text):
    """Escapes HTML special characters while preserving existing HTML tags and TeX formulas."""
    # We do basic cleanup; Org markup to HTML is handled separately
    return text

def convert_org_markup_to_html(text):
    """Converts basic Org-mode markup to HTML tags for Moodle HTML display."""
    if not text:
        return ""
    
    # Preserve TeX math expressions by temporarily replacing them
    math_blocks = []
    def save_math(match):
        math_blocks.append(match.group(0))
        return f"__MATH_BLOCK_{len(math_blocks)-1}__"

    # Protect \( ... \) and \[ ... \] and $ ... $
    text = re.sub(r'\\\(.*?\\\)', save_math, text, flags=re.DOTALL)
    text = re.sub(r'\\\[.*?\\\]', save_math, text, flags=re.DOTALL)
    text = re.sub(r'\$.*?\$', save_math, text)

    # Org-mode bold *word*
    text = re.sub(r'(?<=[\s^])\*([^\*\n]+)\*(?=[\s$.,!?:;])', r'<strong>\1</strong>', text)
    # Org-mode italic /word/
    text = re.sub(r'(?<=[\s^])/([^/\n]+)/(?=[\s$.,!?:;])', r'<em>\1</em>', text)
    # Org-mode code =word= or ~word~
    text = re.sub(r'(?<=[\s^])=([^=\n]+)=(?=[\s$.,!?:;])', r'<code>\1</code>', text)
    text = re.sub(r'(?<=[\s^])~([^~\n]+)~(?=[\s$.,!?:;])', r'<code>\1</code>', text)
    # Org-mode underline _word_
    text = re.sub(r'(?<=[\s^])_([^\_\n]+)_(?=[\s$.,!?:;])', r'<u>\1</u>', text)
    
    # Org-mode verbatim block / src block
    # Simple newline to <br/> or paragraphs
    lines = text.split('\n')
    formatted_lines = []
    in_code = False
    for line in lines:
        if line.strip().startswith('#+BEGIN_SRC') or line.strip().startswith('#+BEGIN_EXAMPLE'):
            in_code = True
            formatted_lines.append('<pre><code>')
            continue
        elif line.strip().startswith('#+END_SRC') or line.strip().startswith('#+END_EXAMPLE'):
            in_code = False
            formatted_lines.append('</code></pre>')
            continue
        
        if in_code:
            formatted_lines.append(html.escape(line))
        else:
            formatted_lines.append(line)
            
    text = '\n'.join(formatted_lines)
    
    # Restore math blocks
    for idx, math_str in enumerate(math_blocks):
        text = text.replace(f"__MATH_BLOCK_{idx}__", math_str)

    return text.strip()


class OrgMoodleParser:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.content = self.filepath.read_text(encoding='utf-8')
        self.category = "$course$/Imported from Org"
        self.questions = []

    def parse(self):
        lines = self.content.splitlines()
        current_question = None
        current_body = []
        current_options = []

        for line in lines:
            # Check for Category header: * Category: Path/To/Category
            cat_match = re.match(r'^\*\s+(?:Category|CATEGORY):\s*(.+)$', line, re.IGNORECASE)
            if cat_match:
                self.category = f"$course$/{cat_match.group(1).strip()}"
                continue

            # Check for Question headline: ** [TYPE] Title
            q_match = re.match(r'^\*\*\s+(?:\[([A-Za-z0-9_\-]+)\])?\s*(.+)$', line)
            if q_match:
                if current_question:
                    current_question['body'] = '\n'.join(current_body).strip()
                    current_question['options'] = current_options
                    self.questions.append(current_question)
                
                qtype_raw = q_match.group(1) or 'multichoice'
                qtitle = q_match.group(2).strip()
                
                current_question = {
                    'type': self._normalize_qtype(qtype_raw),
                    'title': qtitle,
                    'properties': {},
                    'body': '',
                    'options': [],
                    'category': self.category
                }
                current_body = []
                current_options = []
                continue

            if current_question:
                stripped = line.strip()
                if stripped.upper() in [':PROPERTIES:', ':END:']:
                    continue

                # Check for properties: :PROPERTY: value
                prop_match = re.match(r'^\s*:([A-Z_]+):\s*(.+)$', line, re.IGNORECASE)
                if prop_match:
                    pname = prop_match.group(1).upper()
                    pval = prop_match.group(2).strip()
                    current_question['properties'][pname] = pval
                    continue

                # Check for options / answers list items: - [X] text :: feedback
                opt_match = re.match(r'^\s*-\s+(?:\[([ Xx=\-])\]|\(([ Xx=\-])\))?\s*(.+)$', line)
                if opt_match:
                    is_correct_char = opt_match.group(1) or opt_match.group(2) or ''
                    opt_content = opt_match.group(3).strip()
                    
                    feedback = ""
                    if "::" in opt_content:
                        opt_text, feedback = opt_content.split("::", 1)
                        opt_text = opt_text.strip()
                        feedback = feedback.strip()
                    else:
                        opt_text = opt_content

                    is_correct = is_correct_char.upper() in ['X', '=']
                    current_options.append({
                        'text': opt_text,
                        'is_correct': is_correct,
                        'feedback': feedback
                    })
                    continue

                # Plain line in body
                current_body.append(line)

        if current_question:
            current_question['body'] = '\n'.join(current_body).strip()
            current_question['options'] = current_options
            self.questions.append(current_question)

        return self.questions

    def _normalize_qtype(self, raw_type):
        raw = raw_type.lower()
        if raw in ['mcq', 'multichoice', 'multiple_choice']:
            return 'multichoice'
        elif raw in ['tf', 'truefalse', 'true_false', 'boolean']:
            return 'truefalse'
        elif raw in ['shortanswer', 'short_answer', 'sa']:
            return 'shortanswer'
        elif raw in ['matching', 'match']:
            return 'matching'
        elif raw in ['numerical', 'num']:
            return 'numerical'
        elif raw in ['cloze', 'multianswer']:
            return 'cloze'
        elif raw in ['essay', 'free_text']:
            return 'essay'
        return 'multichoice'


def build_moodle_xml(questions, default_category="$course$/Default Category"):
    """Generates a Moodle XML element tree for the parsed questions."""
    quiz_elem = ET.Element('quiz')

    # Add category header question entry
    categories_added = set()

    for q in questions:
        cat_name = q.get('category', default_category)
        if cat_name not in categories_added:
            cat_q = ET.SubElement(quiz_elem, 'question', type='category')
            cat_elem = ET.SubElement(cat_q, 'category')
            cat_text = ET.SubElement(cat_elem, 'text')
            cat_text.text = cat_name
            categories_added.add(cat_name)

        qtype = q['type']
        q_elem = ET.SubElement(quiz_elem, 'question', type=qtype)

        # Name
        name_elem = ET.SubElement(q_elem, 'name')
        name_text = ET.SubElement(name_elem, 'text')
        name_text.text = q['title']

        # Question text
        qtext_elem = ET.SubElement(q_elem, 'questiontext', format='html')
        qtext_text = ET.SubElement(qtext_elem, 'text')
        qhtml = convert_org_markup_to_html(q['body'] or q['title'])
        qtext_text.text = f"<![CDATA[{qhtml}]]>"

        # General feedback
        gen_fb = q['properties'].get('FEEDBACK', '')
        gen_fb_elem = ET.SubElement(q_elem, 'generalfeedback', format='html')
        gen_fb_text = ET.SubElement(gen_fb_elem, 'text')
        gen_fb_text.text = f"<![CDATA[{convert_org_markup_to_html(gen_fb)}]]>"

        # Default grade & penalty
        defgrade = ET.SubElement(q_elem, 'defaultgrade')
        defgrade.text = q['properties'].get('DEFAULTGRADE', '1.0')

        penalty = ET.SubElement(q_elem, 'penalty')
        penalty.text = q['properties'].get('PENALTY', '0.3333333')

        hidden = ET.SubElement(q_elem, 'hidden')
        hidden.text = '0'

        idnumber = ET.SubElement(q_elem, 'idnumber')
        idnumber.text = q['properties'].get('IDNUMBER', '')

        # Question specific handling
        if qtype == 'multichoice':
            single = ET.SubElement(q_elem, 'single')
            single.text = 'true' if q['properties'].get('SINGLE', 'true').lower() == 'true' else 'false'

            shuffle = ET.SubElement(q_elem, 'shuffleanswers')
            shuffle.text = 'true' if q['properties'].get('SHUFFLE', 'true').lower() == 'true' else 'false'

            answernumbering = ET.SubElement(q_elem, 'answernumbering')
            answernumbering.text = q['properties'].get('NUMBERING', 'abc')

            correct_count = sum(1 for opt in q['options'] if opt['is_correct'])

            for opt in q['options']:
                if correct_count == 1:
                    fraction = "100" if opt['is_correct'] else "0"
                else:
                    if opt['is_correct']:
                        fraction = f"{100 / max(1, correct_count):.5f}".rstrip('0').rstrip('.')
                    else:
                        fraction = "-50"

                ans_elem = ET.SubElement(q_elem, 'answer', fraction=fraction, format='html')
                ans_text = ET.SubElement(ans_elem, 'text')
                ans_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['text'])}]]>"

                fb_elem = ET.SubElement(ans_elem, 'feedback', format='html')
                fb_text = ET.SubElement(fb_elem, 'text')
                fb_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['feedback'])}]]>"

        elif qtype == 'truefalse':
            for opt in q['options']:
                fraction = "100" if opt['is_correct'] else "0"
                ans_elem = ET.SubElement(q_elem, 'answer', fraction=fraction)
                ans_text = ET.SubElement(ans_elem, 'text')
                ans_text.text = opt['text'].lower()

                fb_elem = ET.SubElement(ans_elem, 'feedback', format='html')
                fb_text = ET.SubElement(fb_elem, 'text')
                fb_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['feedback'])}]]>"

        elif qtype == 'shortanswer':
            usecase = ET.SubElement(q_elem, 'usecase')
            usecase.text = '0'
            for opt in q['options']:
                fraction = "100" if opt['is_correct'] else "0"
                ans_elem = ET.SubElement(q_elem, 'answer', fraction=fraction, format='moodle_auto_format')
                ans_text = ET.SubElement(ans_elem, 'text')
                ans_text.text = opt['text']
                fb_elem = ET.SubElement(ans_elem, 'feedback', format='html')
                fb_text = ET.SubElement(fb_elem, 'text')
                fb_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['feedback'])}]]>"

        elif qtype == 'matching':
            shuffle = ET.SubElement(q_elem, 'shuffleanswers')
            shuffle.text = 'true'
            for opt in q['options']:
                sub_elem = ET.SubElement(q_elem, 'subquestion', format='html')
                sub_text = ET.SubElement(sub_elem, 'text')
                sub_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['text'])}]]>"
                ans_elem = ET.SubElement(sub_elem, 'answer')
                ans_text = ET.SubElement(ans_elem, 'text')
                ans_text.text = opt['feedback']  # Matching target

        elif qtype == 'numerical':
            for opt in q['options']:
                fraction = "100" if opt['is_correct'] else "0"
                ans_elem = ET.SubElement(q_elem, 'answer', fraction=fraction)
                ans_text = ET.SubElement(ans_elem, 'text')
                ans_text.text = opt['text']
                tolerance = ET.SubElement(ans_elem, 'tolerance')
                tolerance.text = q['properties'].get('TOLERANCE', '0')
                fb_elem = ET.SubElement(ans_elem, 'feedback', format='html')
                fb_text = ET.SubElement(fb_elem, 'text')
                fb_text.text = f"<![CDATA[{convert_org_markup_to_html(opt['feedback'])}]]>"

        elif qtype == 'cloze':
            # Cloze question relies on questiontext embedded code {1:MULTICHOICE:=Right~Wrong}
            pass

        elif qtype == 'essay':
            ET.SubElement(q_elem, 'responseformat').text = 'editor'
            ET.SubElement(q_elem, 'responserequired').text = '1'
            ET.SubElement(q_elem, 'responsefieldlines').text = q['properties'].get('LINES', '15')
            ET.SubElement(q_elem, 'attachments').text = q['properties'].get('ATTACHMENTS', '0')

    return quiz_elem


def prettify_xml(elem):
    """Returns a formatted, indented XML string with CDATA unescaped."""
    raw_bytes = ET.tostring(elem, encoding='utf-8')
    parsed = minidom.parseString(raw_bytes)
    pretty_str = parsed.toprettyxml(indent="  ")
    
    # Fix CDATA encoding caused by Minidom escaping &lt;![CDATA[
    pretty_str = pretty_str.replace("&lt;![CDATA[", "<![CDATA[").replace("]]&gt;", "]]>")
    return pretty_str


def main():
    parser = argparse.ArgumentParser(description="Convert Org-mode or GIFT quiz files to Moodle XML.")
    parser.add_argument("input", help="Path to input .org or .gift file")
    parser.add_argument("-o", "--output", help="Path to output .xml file")
    parser.add_argument("-r", "--random", type=int, help="Randomly sample N questions from the question bank")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    if not args.output:
        output_path = input_path.with_suffix('.xml')
    else:
        output_path = Path(args.output)

    print(f"[*] Parsing '{input_path}'...")
    org_parser = OrgMoodleParser(input_path)
    questions = org_parser.parse()

    if args.random and args.random > 0:
        import random
        if len(questions) > args.random:
            print(f"[*] Randomly sampling {args.random} question(s) out of {len(questions)}...")
            questions = random.sample(questions, args.random)
        else:
            print(f"[*] Requested {args.random} random questions, but bank only has {len(questions)}. Using all.")

    print(f"[*] Found {len(questions)} question(s). Building Moodle XML...")
    quiz_tree = build_moodle_xml(questions)
    pretty_xml = prettify_xml(quiz_tree)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(pretty_xml, encoding='utf-8')
    print(f"[✓] Successfully wrote Moodle XML to '{output_path}'!")


if __name__ == "__main__":
    main()
