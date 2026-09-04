# Emacs Moodle Infrastructure (`emacs-moodle`)

A complete, portable, native-first infrastructure for authoring, managing, and building **Moodle pedagogical artifacts** (quizzes, question banks, lessons, cloze exercises, essay prompts) directly inside **Emacs** using plain-text **Org-mode**.

---

## 🌟 Key Features
- **Single Source of Truth**: Draft all course material (lessons, quizzes, formulas, code snippets) in plain-text Org files.
- **Multi-Format Moodle Export**:
  - **Moodle XML** (`.xml`): Full-featured native Moodle format supporting HTML, TeX math, categories, feedback, default grades, penalties, essay properties, and matching pairs.
  - **GIFT Format** (`.gift`): Plain-text question bank format for fast Moodle Question Bank import.
  - **Moodle Lesson HTML**: Clean HTML pages ready for embedding into Moodle Lesson modules.
- **Seamless Emacs Integration**:
  - `emacs-moodle-mode`: Minor mode with keybindings (`C-c m x`, `C-c m g`, `C-c m i *`).
  - Automated project setup via `.dir-locals.el`.
  - YASnippet templates for MCQ, Short Answer, Matching, True/False, Numerical, Cloze, and Essay.
- **Zero-Dependency Portability**: Built with standard Python 3 and Emacs Lisp. Works on Linux, macOS, and Windows.

---

## 📁 Repository Structure

```
emacs-moodle/
├── README.md                      # Infrastructure overview and documentation
├── QUICKSTART.md                  # Quickstart guide
├── FAQ.md                         # Frequently Asked Questions (SCORM, Moodle XML, GIFT, etc.)
├── docs/                          # Comprehensive in-depth documentation
│   └── SCORM_TUTORIAL.md          # Complete guide for generating and importing SCORM packages
├── init.el                        # Standalone Emacs setup with MELPA & dev packages
├── Makefile                       # Automated build and validation targets
├── .dir-locals.el                 # Automated Emacs setup upon opening workspace
├── elisp/
│   └── emacs-moodle.el            # Emacs Lisp package & minor mode
├── scripts/
│   ├── build_scorm.py             # Generates standard SCORM 1.2 packages (.zip)
│   ├── org_to_moodle_xml.py       # Converts Org-mode quiz files to Moodle XML
│   ├── org_to_gift.py             # Converts Org-mode quiz files to GIFT format
│   └── gift_validator.py          # GIFT syntax validator
├── snippets/
│   └── moodle-mode/               # YASnippet templates for question types
├── content/
│   ├── quizzes/                   # Source Org-mode question banks
│   └── lessons/                   # Source Org-mode lesson contents
└── dist/                          # Generated output artifacts (.xml, .gift, .html)
    ├── xml/
    ├── gift/
    └── lessons/
```

---

## 🚀 Quick Usage inside Emacs

1. Open any Org file in `content/quizzes/` or `content/lessons/`.
2. `emacs-moodle-mode` activates automatically via `.dir-locals.el`.
3. Use keybindings to insert templates or export artifacts:
   - `C-c m x` : Export current buffer to **Moodle XML** (`dist/xml/`).
   - `C-c m g` : Export current buffer to **GIFT format** (`dist/gift/`).
   - `C-c m i m` : Insert **Multiple Choice Question** template.
   - `C-c m i t` : Insert **True/False** template.
   - `C-c m i s` : Insert **Short Answer** template.
   - `C-c m i k` : Insert **Matching** template.
   - `C-c m i n` : Insert **Numerical** template.
   - `C-c m i e` : Insert **Essay** template.

---

## 🧰 Standalone Emacs Launch

You can launch Emacs with this project's standalone `init.el` configuration (which automatically bootstraps MELPA, Vertico, Magit, YASnippet, and Company) by running:

```bash
emacs -q -l init.el content/quizzes/sample_quiz.org
```

---

## 🛠️ CLI Automation via `Makefile`

Build all artifacts across your entire repository with a single command:

```bash
# Build all XML, GIFT, and Lesson HTML files
make build

# Validate GIFT syntax
make validate

# Clean build outputs
make clean
```

---

## 📥 Importing into Moodle

1. Log into your **Moodle Course**.
2. Go to **Course Administration** > **Question Bank** > **Import**.
3. Select **Moodle XML format** (or **GIFT format**).
4. Upload your generated `.xml` or `.gift` file from `dist/xml/` or `dist/gift/`.
5. Click **Import**! All questions will be categorized and ready to add to any Quiz activity.
