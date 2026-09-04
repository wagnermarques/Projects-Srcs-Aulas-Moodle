# Frequently Asked Questions (FAQ) - Emacs Moodle Infrastructure

---

## 📌 General & Architecture

### Q1: Is it possible to use SCORM to import each specific artifact or all artifacts at once into Moodle?

**Yes, absolutely.** SCORM (*Sharable Content Object Reference Model*, versions 1.2 and 2004) supports both granular and monolithic deployment strategies:

1. **Per-Artifact Import (Single-SCO Package):**
   - You can package an individual lesson (e.g., `docker1/index.html`) or interactive quiz into a standalone `.zip` containing an `imsmanifest.xml` descriptor.
   - In Moodle, you add each package as an independent **SCORM package** (`mod_scorm`) activity under separate topic sections.

2. **All Artifacts at Once (Multi-SCO Course Package):**
   - You can package all lesson pages, code tutorials, and interactive quizzes into a **single SCORM `.zip` package**.
   - The `imsmanifest.xml` defines an organizational tree (Table of Contents).
   - In Moodle, the SCORM player displays a navigable sidebar with all modules, chapters, and quizzes, passing unified tracking (completion, time spent, mastery score) back to the Moodle Gradebook.

---

### Q2: SCORM vs. Native Moodle Formats (Moodle XML, GIFT, MBZ): Which should I choose?

| Feature / Criteria            | **SCORM Package (`.zip`)**                            | **Moodle XML / GIFT**                              | **Moodle Course Backup (`.mbz`)**       |
|-------------------------------|-------------------------------------------------------|----------------------------------------------------|-----------------------------------------|
| **Portability**               | Universal (works on Moodle, Canvas, Blackboard, etc.) | Moodle Question Bank                               | Moodle Courses only                     |
| **All-in-One Import**         | ✅ Yes (Multi-SCO `.zip`)                             | ❌ Imports questions to Bank                       | ✅ Yes (Restores full course structure) |
| **Question Bank Integration** | ❌ No (contained in SCORM player)                     | ✅ Full (questions reusable in native Quizzes)     | ✅ Full (includes activities & bank)    |
| **Native Moodle Features**    | Basic (gradebook passback)                            | Full (shuffling, question variants, adaptive mode) | Full (native Moodle experience)         |
| **Hosting & Rendering**       | Self-contained iframe/player                          | Rendered natively by Moodle theme                  | Rendered natively by Moodle theme       |

> **Recommendation:**
> - Use **Moodle XML (`.xml`)** or **GIFT (`.gift`)** when you want questions stored in Moodle's native **Question Bank** for maximum flexibility, security, and reusability.
> - Use **Moodle MBZ (`.mbz`)** to deploy entire course structures (Lessons, Quizzes, Categories) in a single restore step.
> - Use **SCORM (`.zip`)** when creating standalone interactive learning modules with cross-LMS portability or self-contained navigation.
> 
> 📖 *For a complete step-by-step tutorial on generating and importing SCORM packages into Moodle, see [docs/SCORM_TUTORIAL.md](docs/SCORM_TUTORIAL.md).*

---

## 🛠️ Authoring & Building

### Q3: How do I export an Org-mode question bank to Moodle XML or GIFT?

Inside Emacs with `emacs-moodle-mode` active:
- Press `C-c m x` to export to **Moodle XML**.
- Press `C-c m g` to export to **GIFT format**.

From the command line / terminal:
```bash
# Convert to Moodle XML
python3 scripts/org_to_moodle_xml.py content/quizzes/my_quiz.org -o dist/xml/my_quiz.xml

# Convert to GIFT format
python3 scripts/org_to_gift.py content/quizzes/my_quiz.org -o dist/gift/my_quiz.gift

# Validate GIFT syntax
python3 scripts/gift_validator.py dist/gift/my_quiz.gift
```

---

### Q4: How do I convert an Org-mode tutorial into Lesson HTML?

You can export directly with Emacs batch mode:
```bash
emacs content/lessons/my_lesson.org --batch --eval "(progn (require 'ox-html) (org-html-export-to-html))"
```
Or use the automated `Makefile` target:
```bash
make lessons
```

---

### Q5: How do I import the generated question banks into my Moodle course?

1. Navigate to your course (e.g. `https://your-moodle.com/course/view.php?id=...`).
2. Go to **Course Administration / Gear Icon** > **Question Bank (Banco de Questões)** > **Import (Importar)**.
3. Select **Moodle XML format** (or **GIFT format**).
4. Upload the generated `.xml` or `.gift` file.
5. Click **Import**. All questions with categories, points, tags, and feedback will be created in your Question Bank.

---

## 🐙 GitHub & External Repository Integration

### Q6: What strategies and possibilities exist to integrate external GitHub repositories (e.g., `aulas_de_docker`) with course artifacts and Moodle?

Integrating a dedicated GitHub repository like [aulas_de_docker](https://github.com/wagnermarques/aulas_de_docker) provides several powerful pedagogical and operational workflows:

#### 1. 🔄 Code-Base Synchronization (Git Remote / Submodule / Subtree)
- **Git Subtree / Submodule:** Mount the external repository directly inside your course workspace (e.g., `git submodule add https://github.com/wagnermarques/aulas_de_docker docker1` or `git subtree`).
- **Dedicated Lab Files:** Keep runnable examples (`Dockerfile`, `docker-compose.yml`, sample Python/Node apps) in the GitHub repository so students can clone the exact lab setup locally with:
  ```bash
  git clone https://github.com/wagnermarques/aulas_de_docker.git
  ```

#### 2. ⚡ CI/CD Automation with GitHub Actions
- Configure a GitHub Action in `.github/workflows/build-moodle.yml` that triggers on every `git push`:
  - **Auto-compiles** all Org files to **Moodle XML**, **GIFT**, and **Lesson HTML**.
  - **Validates** GIFT syntax automatically.
  - **Publishes GitHub Releases** with attached `.xml`, `.gift`, and `.mbz` ready-to-import bundles.
  - **Deploys Lesson HTML to GitHub Pages** (`https://<user>.github.io/<repo>`), allowing you to embed live, interactive documentation directly inside Moodle via iFrame or URL Resource.

#### 3. ☁️ One-Click Cloud Labs via GitHub Codespaces / Dev Containers
- Add a `.devcontainer/devcontainer.json` or `Dockerfile` to the repository.
- Place a **"Open in GitHub Codespaces"** badge in your Moodle course page and lesson files.
- Students click the link in Moodle and immediately receive a fully configured, browser-based Linux + Docker terminal without needing to install anything on their local machine.

#### 4. 🔗 Dynamic Moodle Links & Resource Embedding
- **Raw File Downloads:** Embed direct raw links in Moodle to configuration files (`https://raw.githubusercontent.com/wagnermarques/aulas_de_docker/main/docker-compose.yml`).
- **Release Assets:** Link Moodle activities directly to versioned release packages (`v1.0.0.zip`).
- **Live Markdown / HTML Rendering:** Embed rendered tutorials using Moodle's **External URL** activity or **Page / iFrame** embedding.
