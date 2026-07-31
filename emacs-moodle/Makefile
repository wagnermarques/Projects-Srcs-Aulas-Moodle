# Makefile for Emacs Moodle Infrastructure
# Author: Emacs Moodle Infrastructure

PYTHON := python3
SCRIPTS_DIR := scripts
CONTENT_DIR := content
DIST_DIR := dist

QUIZ_SRCS := $(wildcard $(CONTENT_DIR)/quizzes/*.org)
XML_OUTS := $(patsubst $(CONTENT_DIR)/quizzes/%.org,$(DIST_DIR)/xml/%.xml,$(QUIZ_SRCS))
GIFT_OUTS := $(patsubst $(CONTENT_DIR)/quizzes/%.org,$(DIST_DIR)/gift/%.gift,$(QUIZ_SRCS))
MBZ_OUTS := $(patsubst $(CONTENT_DIR)/quizzes/%.org,$(DIST_DIR)/mbz/%.mbz,$(QUIZ_SRCS))

LESSON_SRCS := $(wildcard $(CONTENT_DIR)/lessons/*.org)
LESSON_HTMLS := $(patsubst $(CONTENT_DIR)/lessons/%.org,$(DIST_DIR)/lessons/%.html,$(LESSON_SRCS))

.PHONY: all build quizzes gift mbz lessons courses validate clean help

all: build validate

build: quizzes gift mbz lessons courses

courses:
	@echo "[*] Running Automated Batch Moodle Course Builder..."
	$(PYTHON) $(SCRIPTS_DIR)/build_all_courses.py 2026Sem2-AuxDomiciliar/lcd

quizzes: $(XML_OUTS)

gift: $(GIFT_OUTS)

mbz: $(MBZ_OUTS)

lessons: $(LESSON_HTMLS)

$(DIST_DIR)/xml/%.xml: $(CONTENT_DIR)/quizzes/%.org
	@mkdir -p $(DIST_DIR)/xml
	@echo "[*] Building Moodle XML for $<..."
	$(PYTHON) $(SCRIPTS_DIR)/org_to_moodle_xml.py $< -o $@

$(DIST_DIR)/gift/%.gift: $(CONTENT_DIR)/quizzes/%.org
	@mkdir -p $(DIST_DIR)/gift
	@echo "[*] Building GIFT for $<..."
	$(PYTHON) $(SCRIPTS_DIR)/org_to_gift.py $< -o $@

$(DIST_DIR)/mbz/%.mbz: $(CONTENT_DIR)/quizzes/%.org
	@mkdir -p $(DIST_DIR)/mbz
	@echo "[*] Packaging Moodle MBZ for $<..."
	$(PYTHON) $(SCRIPTS_DIR)/moodle_packager.py $< -o $@

$(DIST_DIR)/lessons/%.html: $(CONTENT_DIR)/lessons/%.org
	@mkdir -p $(DIST_DIR)/lessons
	@echo "[*] Exporting Lesson HTML for $<..."
	emacs $< --batch --eval "(progn (require 'ox-html) (org-html-export-to-html))"
	@mv $(CONTENT_DIR)/lessons/*.html $(DIST_DIR)/lessons/ 2>/dev/null || true

validate: gift
	@echo "[*] Running GIFT syntax validation..."
	@$(PYTHON) $(SCRIPTS_DIR)/gift_validator.py $(DIST_DIR)/gift/*.gift

clean:
	@echo "[*] Cleaning build output directory..."
	rm -rf $(DIST_DIR)

help:
	@echo "Emacs Moodle Infrastructure Build Targets:"
	@echo "  make build     - Build all Moodle XML, GIFT, and Lesson HTML files"
	@echo "  make quizzes   - Generate Moodle XML question banks"
	@echo "  make gift      - Generate GIFT format text question banks"
	@echo "  make lessons   - Export Org lessons to HTML"
	@echo "  make validate  - Validate GIFT question bank files"
	@echo "  make clean     - Remove all generated files in dist/"
