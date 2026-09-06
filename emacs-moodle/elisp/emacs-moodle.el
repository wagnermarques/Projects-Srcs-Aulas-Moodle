;;; emacs-moodle.el --- Emacs infrastructure for Moodle pedagogical artifacts -*- lexical-binding: t; -*-

;; Author: Emacs Moodle Infrastructure
;; Keywords: moodle, org-mode, pedagogy, quiz, gift, xml
;; Version: 1.0.0

;;; Commentary:
;; Major/minor mode tools for authoring Moodle quizzes, question banks, and
;; lessons directly in Emacs using Org-mode. Supports exporting to native
;; Moodle XML and GIFT formats.

(require 'org)
(require 'ob-java nil t)
(require 'ob-rust nil t)

(when (fboundp 'org-babel-do-load-languages)
  (org-babel-do-load-languages
   'org-babel-load-languages
   '((java . t)
     (rust . t)
     (shell . t)
     (emacs-lisp . t)
     (python . t))))

(defgroup emacs-moodle nil
  "Customizations for Emacs Moodle infrastructure."
  :prefix "emacs-moodle-"
  :group 'org)

(defcustom emacs-moodle-script-dir
  (expand-file-name "../scripts" (file-name-directory (or load-file-name buffer-file-name)))
  "Directory containing the Python helper scripts."
  :type 'directory
  :group 'emacs-moodle)

(defcustom emacs-moodle-output-dir
  (expand-file-name "../dist" (file-name-directory (or load-file-name buffer-file-name)))
  "Output directory for generated XML and GIFT files."
  :type 'directory
  :group 'emacs-moodle)

;;;###autoload
(defun emacs-moodle-export-to-xml ()
  "Export the current Org buffer to Moodle XML format."
  (interactive)
  (unless (buffer-file-name)
    (user-error "Buffer must be saved to a file before exporting"))
  (save-buffer)
  (let* ((infile (buffer-file-name))
         (outdir (expand-file-name "xml" emacs-moodle-output-dir))
         (outfile (expand-file-name (concat (file-name-base infile) ".xml") outdir))
         (script (expand-file-name "org_to_moodle_xml.py" emacs-moodle-script-dir))
         (cmd (format "python3 %s %s -o %s"
                      (shell-quote-argument script)
                      (shell-quote-argument infile)
                      (shell-quote-argument outfile))))
    (make-directory outdir t)
    (message "Exporting Moodle XML...")
    (if (zerop (shell-command cmd "*Moodle Export Log*"))
        (message "Successfully exported Moodle XML to %s" outfile)
      (pop-to-buffer "*Moodle Export Log*")
      (error "Moodle XML export failed. Check *Moodle Export Log*"))))

;;;###autoload
(defun emacs-moodle-export-to-gift ()
  "Export the current Org buffer to Moodle GIFT format."
  (interactive)
  (unless (buffer-file-name)
    (user-error "Buffer must be saved to a file before exporting"))
  (save-buffer)
  (let* ((infile (buffer-file-name))
         (outdir (expand-file-name "gift" emacs-moodle-output-dir))
         (outfile (expand-file-name (concat (file-name-base infile) ".gift") outdir))
         (script (expand-file-name "org_to_gift.py" emacs-moodle-script-dir))
         (cmd (format "python3 %s %s -o %s"
                      (shell-quote-argument script)
                      (shell-quote-argument infile)
                      (shell-quote-argument outfile))))
    (make-directory outdir t)
    (message "Exporting GIFT format...")
    (if (zerop (shell-command cmd "*Moodle Export Log*"))
        (message "Successfully exported GIFT format to %s" outfile)
      (pop-to-buffer "*Moodle Export Log*")
      (error "GIFT export failed. Check *Moodle Export Log*"))))

;;;###autoload
(defun emacs-moodle-package-to-mbz ()
  "Package the current Org buffer into a Moodle Activity MBZ file."
  (interactive)
  (unless (buffer-file-name)
    (user-error "Buffer must be saved to a file before packaging"))
  (save-buffer)
  (let* ((infile (buffer-file-name))
         (outdir (expand-file-name "mbz" emacs-moodle-output-dir))
         (outfile (expand-file-name (concat (file-name-base infile) ".mbz") outdir))
         (script (expand-file-name "moodle_packager.py" emacs-moodle-script-dir))
         (cmd (format "python3 %s %s -o %s"
                      (shell-quote-argument script)
                      (shell-quote-argument infile)
                      (shell-quote-argument outfile))))
    (make-directory outdir t)
    (message "Generating Moodle MBZ Package...")
    (if (zerop (shell-command cmd "*Moodle Export Log*"))
        (message "Successfully generated MBZ package at %s" outfile)
      (pop-to-buffer "*Moodle Export Log*")
      (error "MBZ Packaging failed. Check *Moodle Export Log*"))))

;;;###autoload
(defun emacs-moodle-build-course-folder ()
  "Automatically compile all Org lessons/quizzes in current folder and package a Moodle Course (.mbz)."
  (interactive)
  (let* ((target (if (derived-mode-p 'dired-mode)
                     (dired-get-filename nil t)
                   nil))
         (folder (cond
                  ((and target (file-directory-p target)) target)
                  ((derived-mode-p 'dired-mode) (dired-current-directory))
                  (t (file-name-directory (or buffer-file-name default-directory)))))
         (script (expand-file-name "build_all_courses.py" emacs-moodle-script-dir))
         (cmd (format "python3 %s %s"
                      (shell-quote-argument script)
                      (shell-quote-argument folder))))
    (message "Building Moodle Course Package for %s..." folder)
    (if (zerop (shell-command cmd "*Moodle Export Log*"))
        (message "Successfully built Moodle Course Package for %s!" folder)
      (pop-to-buffer "*Moodle Export Log*")
      (error "Course packaging failed. Check *Moodle Export Log*"))))

;; Bind key in Dired mode if loaded
(with-eval-after-load 'dired
  (define-key dired-mode-map (kbd "C-c m c") #'emacs-moodle-build-course-folder))

;;; Templates insertion
(defun emacs-moodle-insert-mcq ()
  "Insert a Multiple Choice Question (MCQ) Org template."
  (interactive)
  (insert "** [MCQ] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: multichoice\n"
          ":SINGLE: true\n"
          ":SHUFFLE: true\n"
          ":DEFAULTGRADE: 1.0\n"
          ":END:\n"
          "Type your question text here. Math formulas like \\( E = mc^2 \\) are supported.\n\n"
          "- [X] Correct Option :: Feedback explaining why this is correct.\n"
          "- [ ] Incorrect Option 1 :: Explanation of why this is wrong.\n"
          "- [ ] Incorrect Option 2 :: Explanation of why this is wrong.\n\n"))

(defun emacs-moodle-insert-truefalse ()
  "Insert a True/False Question Org template."
  (interactive)
  (insert "** [TF] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: truefalse\n"
          ":DEFAULTGRADE: 1.0\n"
          ":END:\n"
          "Statement to evaluate as True or False.\n\n"
          "- [X] True :: Feedback for True response.\n"
          "- [ ] False :: Feedback for False response.\n\n"))

(defun emacs-moodle-insert-shortanswer ()
  "Insert a Short Answer Question Org template."
  (interactive)
  (insert "** [SA] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: shortanswer\n"
          ":DEFAULTGRADE: 1.0\n"
          ":END:\n"
          "Question prompt expecting a exact text or string answer.\n\n"
          "- [X] Correct Answer Text :: Feedback for correct answer.\n\n"))

(defun emacs-moodle-insert-matching ()
  "Insert a Matching Question Org template."
  (interactive)
  (insert "** [MATCH] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: matching\n"
          ":DEFAULTGRADE: 1.0\n"
          ":END:\n"
          "Match each item on the left with the correct target on the right.\n\n"
          "- Item 1 :: Target 1\n"
          "- Item 2 :: Target 2\n"
          "- Item 3 :: Target 3\n\n"))

(defun emacs-moodle-insert-numerical ()
  "Insert a Numerical Question Org template."
  (interactive)
  (insert "** [NUM] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: numerical\n"
          ":TOLERANCE: 0.05\n"
          ":DEFAULTGRADE: 1.0\n"
          ":END:\n"
          "Calculate the exact numerical value:\n\n"
          "- [X] 42.0 :: Feedback for exact answer within tolerance.\n\n"))

(defun emacs-moodle-insert-essay ()
  "Insert an Essay Question Org template."
  (interactive)
  (insert "** [ESSAY] Question Title Here\n"
          ":PROPERTIES:\n"
          ":TYPE: essay\n"
          ":LINES: 15\n"
          ":ATTACHMENTS: 0\n"
          ":DEFAULTGRADE: 5.0\n"
          ":END:\n"
          "Provide a comprehensive essay response explaining your reasoning:\n\n"))

;;; Keymap & Minor Mode
(defvar emacs-moodle-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c m x") #'emacs-moodle-export-to-xml)
    (define-key map (kbd "C-c m g") #'emacs-moodle-export-to-gift)
    (define-key map (kbd "C-c m p") #'emacs-moodle-package-to-mbz)
    (define-key map (kbd "C-c m c") #'emacs-moodle-build-course-folder)
    (define-key map (kbd "C-c m i m") #'emacs-moodle-insert-mcq)
    (define-key map (kbd "C-c m i t") #'emacs-moodle-insert-truefalse)
    (define-key map (kbd "C-c m i s") #'emacs-moodle-insert-shortanswer)
    (define-key map (kbd "C-c m i k") #'emacs-moodle-insert-matching)
    (define-key map (kbd "C-c m i n") #'emacs-moodle-insert-numerical)
    (define-key map (kbd "C-c m i e") #'emacs-moodle-insert-essay)
    map)
  "Keymap for `emacs-moodle-mode'.")

;;;###autoload
(define-minor-mode emacs-moodle-mode
  "Minor mode for authoring Moodle pedagogical artifacts in Org-mode."
  :init-value nil
  :lighter " Moodle"
  :keymap emacs-moodle-mode-map)

(provide 'emacs-moodle)
;;; emacs-moodle.el ends here
