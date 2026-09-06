((org-mode
  . ((eval . (let ((root (locate-dominating-file default-directory ".dir-locals.el")))
               (let ((moodle-el (expand-file-name "elisp/emacs-moodle.el" root)))
                 (when (file-exists-p moodle-el)
                   (load moodle-el nil t)
                   (emacs-moodle-mode 1)))
               (require 'ob-java nil t)
               (require 'ob-rust nil t)
               (when (fboundp 'org-babel-do-load-languages)
                 (org-babel-do-load-languages
                  'org-babel-load-languages
                  '((java . t)
                    (rust . t)
                    (shell . t)
                    (emacs-lisp . t)
                    (python . t))))))
     (org-confirm-babel-evaluate . nil)
     (indent-tabs-mode . nil))))
