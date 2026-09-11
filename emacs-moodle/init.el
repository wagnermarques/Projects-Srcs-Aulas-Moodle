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

;; Modern completion stack (Vertico + Marginalia + Orderless + Consult)
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

(use-package consult
  :bind
  (("C-s"   . consult-line)
   ("C-x b" . consult-buffer)
   ("M-g g" . consult-goto-line)
   ("M-g M-g" . consult-goto-line)))

;; Which-key for command guidance
(use-package which-key
  :init (which-key-mode 1))

;; ==========================================
;; 3. Core Development Packages
;; ==========================================

;; Magit for Git management
(use-package magit
  :bind ("C-x g" . magit-status))

;; Treemacs file and project navigation
(use-package treemacs
  :hook (emacs-startup . treemacs)
  :bind
  ("M-0"       . treemacs-select-window)
  ("C-x t t"   . treemacs)
  ("C-x t 1"   . treemacs-delete-other-windows)
  ("C-x t d"   . treemacs-select-directory)
  ("C-x t B"   . treemacs-bookmark)
  ("C-x t C-t" . treemacs-find-file)
  ("C-x t M-t" . treemacs-find-tag)
  :config
  (setq treemacs-width 30
        treemacs-is-never-other-window t
        treemacs-show-hidden-files t))

;; Markdown mode for editing documentation
(use-package markdown-mode
  :mode ("\\.md\\'" . markdown-mode))

;; YASnippet for code/template expansions
(use-package yasnippet
  :bind
  (("C-c y i" . yas-insert-snippet)
   ("C-c y n" . yas-new-snippet)
   ("C-c y v" . yas-visit-snippet-file))
  :config
  (let ((proj-snippets (expand-file-name "snippets" (file-name-directory (or load-file-name buffer-file-name default-directory)))))
    (when (file-exists-p proj-snippets)
      (add-to-list 'yas-snippet-dirs proj-snippets)))
  (yas-global-mode 1))

;; YASnippet community snippets library
(use-package yasnippet-snippets
  :after yasnippet)

;; AUCTeX for advanced LaTeX editing
(use-package auctex
  :defer t)

;; Company for auto-completion
(use-package company
  :hook (prog-mode . company-mode)
  :custom
  (company-minimum-prefix-length 1)
  (company-idle-delay 0.1))

;; ob-rust and ob-java Babel execution
(use-package ob-rust)

(use-package org
  :ensure nil ; Built-in with Emacs
  :bind
  (:map org-mode-map
        ("C-c C-x C-v" . org-toggle-inline-images))
  :config
  (require 'org-tempo)
  (add-to-list 'org-structure-template-alist
               '("img" . "#+CAPTION: ?\n#+NAME: fig:?\n#+ATTR_HTML: :width 800px :align center\n#+ATTR_LATEX: :width 0.8\\textwidth :placement [htbp]\n#+ATTR_ORG: :width 600\n[[?]]"))
  (setq org-hide-emphasis-markers t)
  (setq org-support-shift-select t)
  (setq org-confirm-babel-evaluate nil)
  (setq org-image-actual-width nil)
  (org-babel-do-load-languages
   'org-babel-load-languages
   '((python . t)
     (emacs-lisp . t)
     (shell . t)
     (java . t)
     (rust . t))))

;; Load local Moodle mode package
(let ((moodle-pkg (expand-file-name "elisp/emacs-moodle.el"
                                    (file-name-directory (or load-file-name buffer-file-name default-directory)))))
  (when (file-exists-p moodle-pkg)
    (load moodle-pkg)
    (add-hook 'org-mode-hook #'emacs-moodle-mode)))

(provide 'init)
;;; init.el ends here
