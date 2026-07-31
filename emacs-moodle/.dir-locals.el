((org-mode
  . ((eval . (let ((moodle-el (expand-file-name "elisp/emacs-moodle.el"
                                                (locate-dominating-file default-directory ".dir-locals.el"))))
               (when (file-exists-p moodle-el)
                 (load moodle-el nil t)
                 (emacs-moodle-mode 1))))
     (org-confirm-babel-evaluate . nil)
     (indent-tabs-mode . nil))))
