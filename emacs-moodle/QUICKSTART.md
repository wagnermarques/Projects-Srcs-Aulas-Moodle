# Quick Start Guide: Emacs Moodle Infrastructure

Get up and running in **5 minutes** authoring Moodle quizzes and lessons with Emacs!

---

## Step 1: Open the Project in Emacs

Open Emacs and navigate to the project directory:

```bash
emacs content/quizzes/sample_quiz.org
```

Emacs will automatically load `.dir-locals.el` and activate `emacs-moodle-mode` (indicated by `Moodle` in your modeline).

---

## Step 2: Write a Question in Org-mode

Create a headline starting with `* Category: Category/Path` and add questions using `** [TYPE] Title`:

```org
* Category: Computer Science/Data Structures

** [MCQ] Stack Operation Principle
:PROPERTIES:
:TYPE: multichoice
:SINGLE: true
:SHUFFLE: true
:END:
Which access principle defines a **Stack** data structure?

- [X] LIFO (Last In, First Out) :: Correct! Stacks process the last pushed item first.
- [ ] FIFO (First In, First Out) :: Incorrect. FIFO is used by Queues.
- [ ] Random Access :: Incorrect. Arrays support random access.
```

---

## Step 3: Export to Moodle XML or GIFT

- **Inside Emacs**: Press `C-c m x` to generate `dist/xml/sample_quiz.xml`.
- **From Command Line**: Run `make build` in your terminal.

---

## Step 4: Import into Moodle

1. Open your Moodle course in a browser.
2. Go to **Question Bank** -> **Import**.
3. Choose **Moodle XML format** and select `dist/xml/sample_quiz.xml`.
4. Click **Import**. Your questions are ready!
