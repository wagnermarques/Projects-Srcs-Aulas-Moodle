;;; init.el --- Emacs Development Environment for emacs-moodle -*- lexical-binding: t; -*-

;; Author: Emacs Moodle Infrastructure
;; Commentary:
;; Standalone & reproducible Emacs configuration for the emacs-moodle project.
;; Configures MELPA, use-package, Org-mode, YASnippet, Magit, Vertico, and
;; auto-loads the emacs-moodle package.

;;; Code:

;; ==========================================
;; 1. Package Manager Setup (MELPA & GNU ELPA)
;; ==========================================
(require 'package)
(setq package-archives '(("melpa" . "https://melpa.org/packages/")
                         ("gnu"   . "https://elpa.gnu.org/packages/")))
(package-initialize)

(unless package-archive-contents
  (package-refresh-contents))

;; Bootstrapping use-package (built-in in Emacs 29+, fallback for older)
(unless (package-installed-p 'use-package)
  (package-install 'use-package))

(require 'use-package)
(setq use-package-always-ensure t)

;; ==========================================
;; 2. Quality of Life & UI Settings
;; ==========================================
(setq inhibit-startup-message t)
(tool-bar-mode -1)
(menu-bar-mode 1)
(scroll-bar-mode -1)

(column-number-mode 1)
(global-display-line-numbers-mode 1)
(show-paren-mode 1)
(global-auto-revert-mode 1)
(setq make-backup-files nil)
(setq auto-save-default nil)

;; Modern completion stack (Vertico + Marginalia + Orderless)
(use-package vertico
  :init
  (vertico-mode 1))

(use-package marginalia
  :after vertico
  :init
  (marginalia-mode 1))

(use-package orderless
  :custom
  (completion-styles '(orderless basic))
  (completion-category-overrides '((file (styles basic partial-completion)))))

;; Which-key for command guidance
(use-package which-key
  :init (which-key-mode 1))

;; ==========================================
;; 3. Core Development Packages
;; ==========================================

;; Magit for Git management
(use-package magit
  :bind ("C-x g" . magit-status))

;; Markdown mode for editing documentation
(use-package markdown-mode
  :mode ("\\.md\\'" . markdown-mode))

;; YASnippet for code/template expansions
(use-package yasnippet
  :config
  (let ((proj-snippets (expand-file-name "snippets" (file-name-directory (or load-file-name buffer-file-name default-directory)))))
    (when (file-exists-p proj-snippets)
      (add-to-list 'yas-snippet-dirs proj-snippets)))
  (yas-global-mode 1))

;; Company for auto-completion
(use-package company
  :hook (prog-mode . company-mode)
  :custom
  (company-minimum-prefix-length 1)
  (company-idle-delay 0.1))

;; ==========================================
;; 4. Org Mode & Moodle Integration
;; ==========================================
(use-package org
  :ensure nil ; Built-in with Emacs
  :config
  (setq org-hide-emphasis-markers t)
  (setq org-support-shift-select t)
  (setq org-confirm-babel-evaluate nil)
  (org-babel-do-load-languages
   'org-babel-load-languages
   '((python . t)
     (emacs-lisp . t)
     (shell . t))))

;; Load local Moodle mode package
(let ((moodle-pkg (expand-file-name "elisp/emacs-moodle.el"
                                    (file-name-directory (or load-file-name buffer-file-name default-directory)))))
  (when (file-exists-p moodle-pkg)
    (load moodle-pkg)
    (add-hook 'org-mode-hook #'emacs-moodle-mode)))

(provide 'init)
;;; init.el ends here
