#!/usr/bin/env python3
"""
build_scorm.py - Automated Multi-Artifact SCORM 1.2 Package Generator for Moodle
Author: Emacs Moodle Infrastructure
License: MIT

Compiles all lessons (HTML) and quiz files (.org) in a given directory into a
fully-featured, interactive, Multi-SCO SCORM 1.2 zip package with automated
Moodle Gradebook score reporting.
"""

import os
import sys
import re
import html
import json
import zipfile
import argparse
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

SCORM_API_WRAPPER_JS = """/* SCORM 1.2 Lightweight API Wrapper */
var scorm = {
  api: null,
  findAPI: function(win) {
    var findAttempts = 0;
    while ((win.API == null) && (win.parent != null) && (win.parent != win)) {
      findAttempts++;
      if (findAttempts > 500) return null;
      win = win.parent;
    }
    return win.API;
  },
  init: function() {
    this.api = this.findAPI(window);
    if (!this.api && window.opener) {
      this.api = this.findAPI(window.opener);
    }
    if (this.api) {
      this.api.LMSInitialize("");
      this.api.LMSSetValue("cmi.core.lesson_status", "incomplete");
      this.api.LMSCommit("");
    }
  },
  complete: function(score) {
    if (this.api) {
      this.api.LMSSetValue("cmi.core.lesson_status", "completed");
      if (score !== undefined && score !== null) {
        this.api.LMSSetValue("cmi.core.score.raw", Math.round(score).toString());
        this.api.LMSSetValue("cmi.core.score.min", "0");
        this.api.LMSSetValue("cmi.core.score.max", "100");
      }
      this.api.LMSCommit("");
    }
  },
  finish: function() {
    if (this.api) {
      this.api.LMSFinish("");
    }
  }
};

window.addEventListener("load", function() {
  scorm.init();
});

window.addEventListener("beforeunload", function() {
  scorm.finish();
});
"""

def parse_org_quiz(filepath):
    """Parses an Org-mode quiz file into structured questions."""
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()
    
    title_match = re.search(r'^#\+TITLE:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
    quiz_title = title_match.group(1).strip() if title_match else Path(filepath).stem

    questions = []
    current_q = None
    current_body = []
    current_options = []

    for line in lines:
        q_match = re.match(r'^\*\*\s+(?:\[([A-Za-z0-9_\-]+)\])?\s*(.+)$', line)
        if q_match:
            if current_q:
                current_q['body'] = '\n'.join(current_body).strip()
                current_q['options'] = current_options
                questions.append(current_q)
            
            qtype_raw = (q_match.group(1) or 'multichoice').lower()
            qtitle = q_match.group(2).strip()
            
            if qtype_raw in ['mcq', 'multichoice', 'multiplechoice']:
                qtype = 'multichoice'
            elif qtype_raw in ['tf', 'truefalse', 'true_false']:
                qtype = 'truefalse'
            elif qtype_raw in ['sa', 'shortanswer', 'short_answer']:
                qtype = 'shortanswer'
            elif qtype_raw in ['match', 'matching']:
                qtype = 'matching'
            else:
                qtype = 'multichoice'

            current_q = {
                'id': f"q_{len(questions)+1}",
                'type': qtype,
                'title': qtitle,
                'properties': {},
                'body': '',
                'options': []
            }
            current_body = []
            current_options = []
            continue

        if current_q:
            stripped = line.strip()
            if stripped.upper() in [':PROPERTIES:', ':END:']:
                continue
            prop_match = re.match(r'^\s*:([A-Z_]+):\s*(.+)$', line, re.IGNORECASE)
            if prop_match:
                current_q['properties'][prop_match.group(1).upper()] = prop_match.group(2).strip()
                continue
            
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

                if current_q['type'] == 'matching':
                    # Matching pairs are: Left :: Right
                    current_options.append({
                        'left': opt_text,
                        'right': feedback
                    })
                else:
                    is_correct = is_correct_char.upper() in ['X', '=']
                    current_options.append({
                        'text': opt_text,
                        'is_correct': is_correct,
                        'feedback': feedback
                    })
                continue
            
            current_body.append(line)

    if current_q:
        current_q['body'] = '\n'.join(current_body).strip()
        current_q['options'] = current_options
        questions.append(current_q)

    return quiz_title, questions

def generate_interactive_quiz_html(quiz_title, questions):
    """Generates a responsive, interactive HTML quiz with automated grading and SCORM integration."""
    questions_json = json.dumps(questions, ensure_ascii=False)
    
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(quiz_title)}</title>
  <script src="scorm_api.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #1e293b;
      background: #f8fafc;
      margin: 0;
      padding: 30px 15px;
    }}
    .quiz-container {{
      max-width: 820px;
      margin: 0 auto;
      background: #ffffff;
      padding: 32px;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }}
    h1 {{
      color: #0f172a;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 12px;
      margin-top: 0;
    }}
    .q-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
      transition: all 0.2s ease;
    }}
    .q-card.correct {{
      border-left: 5px solid #10b981;
      background: #f0fdf4;
    }}
    .q-card.incorrect {{
      border-left: 5px solid #ef4444;
      background: #fef2f2;
    }}
    .q-title {{
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 10px;
      color: #1e293b;
    }}
    .q-body {{
      margin-bottom: 15px;
      color: #334155;
    }}
    .option-label {{
      display: block;
      padding: 10px 14px;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: background 0.15s ease;
    }}
    .option-label:hover {{
      background: #f1f5f9;
    }}
    .input-text {{
      width: 100%;
      max-width: 400px;
      padding: 10px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 1rem;
    }}
    .match-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      gap: 15px;
    }}
    .match-left {{
      flex: 1;
      font-weight: 500;
    }}
    .match-select {{
      flex: 1;
      padding: 8px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 0.95rem;
    }}
    .feedback-box {{
      margin-top: 12px;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.95rem;
      display: none;
    }}
    .feedback-box.show {{
      display: block;
    }}
    .fb-correct {{
      background: #dcfce7;
      color: #166534;
    }}
    .fb-incorrect {{
      background: #fee2e2;
      color: #991b1b;
    }}
    .btn-submit {{
      background: #0284c7;
      color: #ffffff;
      border: none;
      padding: 14px 28px;
      font-size: 1.05rem;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      width: 100%;
      transition: background 0.2s ease;
    }}
    .btn-submit:hover {{
      background: #0369a1;
    }}
    .score-banner {{
      margin-top: 24px;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      font-size: 1.3rem;
      font-weight: 700;
      display: none;
    }}
  </style>
</head>
<body>
  <div class="quiz-container">
    <h1>📝 {html.escape(quiz_title)}</h1>
    <p>Responda às questões abaixo e clique em <strong>Submeter Respostas</strong> para validar e enviar sua nota para o Moodle.</p>
    
    <div id="questions-root"></div>
    
    <button class="btn-submit" id="btn-submit" onclick="gradeQuiz()">Submeter Respostas</button>
    <div class="score-banner" id="score-banner"></div>
  </div>

  <script>
    const quizData = {questions_json};

    function renderQuiz() {{
      const root = document.getElementById('questions-root');
      root.innerHTML = '';

      quizData.forEach((q, idx) => {{
        const card = document.createElement('div');
        card.className = 'q-card';
        card.id = 'card-' + q.id;

        let contentHtml = `<div class="q-title">Questão ${{idx + 1}}: ${{escapeHtml(q.title)}}</div>`;
        if (q.body) {{
          contentHtml += `<div class="q-body">${{escapeHtml(q.body)}}</div>`;
        }}

        if (q.type === 'multichoice' || q.type === 'truefalse') {{
          q.options.forEach((opt, oIdx) => {{
            contentHtml += `
              <label class="option-label">
                <input type="radio" name="${{q.id}}" value="${{oIdx}}">
                ${{escapeHtml(opt.text)}}
              </label>
            `;
          }});
        }} else if (q.type === 'shortanswer') {{
          contentHtml += `
            <div>
              <input type="text" class="input-text" id="input-${{q.id}}" placeholder="Digite sua resposta...">
            </div>
          `;
        }} else if (q.type === 'matching') {{
          const rights = q.options.map(o => o.right).sort(() => Math.random() - 0.5);
          q.options.forEach((opt, mIdx) => {{
            contentHtml += `
              <div class="match-row">
                <span class="match-left">${{escapeHtml(opt.left)}}</span>
                <select class="match-select" id="match-${{q.id}}-${{mIdx}}">
                  <option value="">-- Escolha a correspondência --</option>
                  ${{rights.map(r => `<option value="${{escapeHtml(r)}}">${{escapeHtml(r)}}</option>`).join('')}}
                </select>
              </div>
            `;
          }});
        }}

        contentHtml += `<div class="feedback-box" id="fb-${{q.id}}"></div>`;
        card.innerHTML = contentHtml;
        root.appendChild(card);
      }});
    }}

    function gradeQuiz() {{
      let total = quizData.length;
      let score = 0;

      quizData.forEach((q, idx) => {{
        const card = document.getElementById('card-' + q.id);
        const fb = document.getElementById('fb-' + q.id);
        let isCorrect = false;
        let feedbackText = "";

        if (q.type === 'multichoice' || q.type === 'truefalse') {{
          const checked = document.querySelector(`input[name="${{q.id}}"]:checked`);
          if (checked) {{
            const optIdx = parseInt(checked.value, 10);
            const opt = q.options[optIdx];
            if (opt.is_correct) {{
              isCorrect = true;
              feedbackText = opt.feedback || "Correto!";
            }} else {{
              feedbackText = opt.feedback || "Incorreto.";
            }}
          }} else {{
            feedbackText = "Nenhuma alternativa selecionada.";
          }}
        }} else if (q.type === 'shortanswer') {{
          const inputVal = (document.getElementById('input-' + q.id).value || '').trim().toLowerCase();
          const correctOpts = q.options.filter(o => o.is_correct || o.text).map(o => o.text.trim().toLowerCase());
          if (correctOpts.includes(inputVal)) {{
            isCorrect = true;
            feedbackText = "Correto!";
          }} else {{
            feedbackText = `Incorreto. Resposta esperada: ${{q.options[0] ? q.options[0].text : ''}}`;
          }}
        }} else if (q.type === 'matching') {{
          let matchAll = true;
          q.options.forEach((opt, mIdx) => {{
            const sel = document.getElementById(`match-${{q.id}}-${{mIdx}}`);
            if (!sel || sel.value !== opt.right) {{
              matchAll = false;
            }}
          }});
          isCorrect = matchAll;
          feedbackText = isCorrect ? "Todas as associações corretas!" : "Algumas associações estão incorretas.";
        }}

        card.className = 'q-card ' + (isCorrect ? 'correct' : 'incorrect');
        fb.className = 'feedback-box show ' + (isCorrect ? 'fb-correct' : 'fb-incorrect');
        fb.innerHTML = feedbackText;

        if (isCorrect) {{
          score++;
        }}
      }});

      const percentage = (score / total) * 100;
      const banner = document.getElementById('score-banner');
      banner.style.display = 'block';
      banner.style.background = percentage >= 60 ? '#ecfdf5' : '#fef2f2';
      banner.style.color = percentage >= 60 ? '#065f46' : '#991b1b';
      banner.style.border = `2px solid ${{percentage >= 60 ? '#10b981' : '#ef4444'}}`;
      banner.innerHTML = `Sua Pontuação: ${{score}} de ${{total}} (${{percentage.toFixed(0)}}%)`;

      // Report score to Moodle SCORM API
      if (typeof scorm !== 'undefined') {{
        scorm.complete(percentage);
      }}
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }}

    window.addEventListener('DOMContentLoaded', renderQuiz);
  </script>
</body>
</html>
"""

def generate_multi_sco_manifest(course_title, items, identifier="COURSE_SCORM_PACKAGE"):
    """
    items is a list of dicts:
    [
      {"identifier": "ITEM_1", "title": "Tutorial: Docker e Containers", "href": "index.html", "files": ["index.html"]},
      {"identifier": "ITEM_2", "title": "Quiz 1: Fundamentos", "href": "quiz1_fundamentos.html", "files": ["quiz1_fundamentos.html"]}
    ]
    """
    manifest = ET.Element('manifest', {
        'identifier': identifier,
        'version': '1.0',
        'xmlns': 'http://www.imsproject.org/xsd/imscp_rootv1p1p2',
        'xmlns:adlcp': 'http://www.adlnet.org/xsd/adlcp_rootv1p2',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd'
    })

    metadata = ET.SubElement(manifest, 'metadata')
    schema = ET.SubElement(metadata, 'schema')
    schema.text = 'ADL SCORM'
    schemaversion = ET.SubElement(metadata, 'schemaversion')
    schemaversion.text = '1.2'

    organizations = ET.SubElement(manifest, 'organizations', {'default': 'ORG_DEFAULT'})
    org = ET.SubElement(organizations, 'organization', {'identifier': 'ORG_DEFAULT'})
    org_title = ET.SubElement(org, 'title')
    org_title.text = course_title

    resources = ET.SubElement(manifest, 'resources')

    for idx, item in enumerate(items, 1):
        item_id = item.get('identifier', f"ITEM_{idx}")
        res_id = f"RES_{idx}"
        
        org_item = ET.SubElement(org, 'item', {
            'identifier': item_id,
            'identifierref': res_id,
            'isvisible': 'true'
        })
        i_title = ET.SubElement(org_item, 'title')
        i_title.text = item.get('title', f"Module {idx}")
        
        res = ET.SubElement(resources, 'resource', {
            'identifier': res_id,
            'type': 'webcontent',
            'adlcp:scormtype': 'sco',
            'href': item.get('href')
        })
        
        for f in item.get('files', [item.get('href')]):
            ET.SubElement(res, 'file', {'href': f})

    xml_str = ET.tostring(manifest, encoding='utf-8')
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="  ", encoding="utf-8")

def build_directory_scorm(directory_path, output_zip, course_title=None):
    """
    Scans a course directory (e.g. docker1/), exports all lessons and quizzes to interactive HTML,
    and packages everything into a Multi-SCO SCORM 1.2 package with a Table of Contents.
    """
    dir_path = Path(directory_path).resolve()
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Directory '{directory_path}' does not exist.")

    if not course_title:
        course_title = f"Curso {dir_path.name.capitalize()} - Módulos & Quizzes"

    print(f"[*] Scanning directory '{dir_path}' for lessons and quizzes...")

    sco_items = []
    generated_files = {} # filename -> string content

    # 1. Look for Lesson files (.org or .html)
    # Check index.org / index.html
    index_html = dir_path / "index.html"
    index_org = dir_path / "index.org"

    if index_org.exists() and not index_html.exists():
        print("[*] Exporting index.org to index.html with Emacs batch...")
        cmd = f'emacs "{index_org}" --batch --eval "(progn (require \'ox-html) (org-html-export-to-html))"'
        subprocess.run(cmd, shell=True, check=False)

    if index_html.exists():
        # Read title from index.org or index.html
        lesson_title = "Tutorial: " + dir_path.name.capitalize()
        if index_org.exists():
            m = re.search(r'^#\+TITLE:\s*(.+)$', index_org.read_text(encoding='utf-8'), re.MULTILINE)
            if m:
                lesson_title = m.group(1).strip()

        # Inject scorm_api.js into index.html if not present
        html_content = index_html.read_text(encoding='utf-8')
        if "scorm_api.js" not in html_content:
            html_content = html_content.replace("</head>", '  <script src="scorm_api.js"></script>\n</head>')
            index_html.write_text(html_content, encoding='utf-8')

        sco_items.append({
            "identifier": "SCO_LESSON_MAIN",
            "title": f"📖 1. {lesson_title}",
            "href": "index.html",
            "files": ["index.html"]
        })
        print(f"  [+] Included Lesson SCO: 'index.html' ({lesson_title})")

    # 2. Look for Quiz files (*quiz*.org or all .org quizzes)
    quiz_files = sorted(dir_path.glob("*.org"))
    quiz_idx = 1

    for qfile in quiz_files:
        if qfile.name == "index.org":
            continue
        
        q_title, questions = parse_org_quiz(qfile)
        if not questions:
            continue
        
        target_html_name = f"{qfile.stem}.html"
        interactive_quiz_html = generate_interactive_quiz_html(q_title, questions)
        
        # Write the interactive quiz html into directory so it's also saved
        (dir_path / target_html_name).write_text(interactive_quiz_html, encoding='utf-8')
        
        quiz_item_title = f"📝 {len(sco_items)+1}. {q_title}"
        sco_items.append({
            "identifier": f"SCO_QUIZ_{quiz_idx}",
            "title": quiz_item_title,
            "href": target_html_name,
            "files": [target_html_name]
        })
        print(f"  [+] Included Quiz SCO: '{target_html_name}' ({q_title} - {len(questions)} questões)")
        quiz_idx += 1

    if not sco_items:
        raise ValueError(f"No lesson or quiz artifacts found in '{dir_path}'.")

    # Generate multi-SCO manifest
    manifest_xml = generate_multi_sco_manifest(course_title, sco_items)

    out_path = Path(output_zip).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('imsmanifest.xml', manifest_xml)
        zf.writestr('scorm_api.js', SCORM_API_WRAPPER_JS)
        
        # Add all files in dir_path except .zip, .org, .xml, .gift
        for root, _, files in os.walk(dir_path):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), dir_path)
                if not rel.endswith('.zip') and not rel.endswith('.org') and not rel.endswith('.xml') and not rel.endswith('.gift'):
                    full_path = Path(root) / f
                    zf.write(full_path, rel)

    print(f"\n[✓] Successfully built Multi-SCO SCORM 1.2 package ({len(sco_items)} SCOs): '{out_path}'")

def main():
    parser = argparse.ArgumentParser(description="Multi-Artifact SCORM 1.2 Package Generator for Moodle")
    parser.add_argument("source", help="Path to course directory (e.g. docker1) or primary HTML file")
    parser.add_argument("-o", "--output", required=True, help="Output .zip file path")
    parser.add_argument("-t", "--title", default=None, help="Title of the SCORM course/module")
    args = parser.parse_args()

    src = Path(args.source)
    if src.is_dir():
        build_directory_scorm(args.source, args.output, args.title)
    else:
        # If single file passed, build single scorm
        build_directory_scorm(src.parent, args.output, args.title)

if __name__ == "__main__":
    main()
