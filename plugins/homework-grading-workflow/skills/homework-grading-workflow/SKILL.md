---
name: homework-grading-workflow
description: Use when processing scanned homework PDFs, organizing student submissions by name, creating individual student files from batched scans, checking homework completion, or updating grading spreadsheets. Handles handwritten name recognition via vision, fuzzy roster matching, session resume for large batches, and checklist generation.
---

# Homework Grading Workflow

## Overview

Automates processing of scanned homework: extract student names from pages using vision, match to roster, create individual PDFs per student, and update completion spreadsheets.

**Core accuracy requirements:**
1. Read EVERY page individually (no batching)
2. Focus on the Name field at TOP of worksheet
3. Verify EACH PDF after creation

## When to Use

**Trigger phrases:**
- "Process this homework PDF"
- "Organize homework by student"
- "Create individual student files from this scan"
- "Update homework checklist"
- "Which students submitted homework"
- "Sort student assignments"
- "Grade these papers"
- "Split this PDF by student"
- "Track homework completion"
- "Who turned in homework"
- "Missing assignments"

**Symptoms this skill addresses:**
- Batched scanned documents with multiple students' work
- Need to identify handwritten names on worksheets
- Teacher grading workflow automation
- Class period tracking and organization
- Assignment submission tracking

**Required inputs:**
- Scanned homework PDF (multiple students' work)
- Student roster spreadsheet (with period sheets)
- Completion spreadsheet (optional, for tracking)

## Workflow Overview

```
Phase 0: Planning (BEFORE ANYTHING ELSE)
├── Count pages in PDF (fitz.open → len(doc))
├── CREATE tracking file with batch plan
├── Calculate sessions needed: ceil(total_pages / 99)
├── Display plan to user:
│   "150 pages = 2 sessions (99 + 51)"
└── User confirms before proceeding

Phase 1: Setup
├── Load roster from xlsx skill
├── Extract PDF pages as images
└── Tracking file already exists from Phase 0

Phase 2: Page Analysis (CRITICAL)
├── Check tracking file for current_session and start_page
├── Read EACH page individually (max 99 per session)
├── Find Name field at top
├── Match to roster (fuzzy matching)
├── Save to tracking file after EACH page
└── Stop at session limit, inform user to resume

Phase 3: User Verification
├── Display uncertain pages
├── User confirms/corrects names
└── All pages must be assigned

Phase 4: Create PDFs
├── Group pages by student
├── Create individual PDFs
└── Skip Unknown pages

Phase 5: Update Spreadsheet
├── Add assignment column
├── Mark submissions with X
└── Update Total formula

Phase 6: Verification
├── Check each PDF has correct pages
├── Cross-reference spreadsheet
└── Cleanup temp files
```

## Quick Reference

| Phase | Reference File | Script/Template |
|-------|---------------|-----------------|
| Decision Flow | [workflow-flowchart.md](reference/workflow-flowchart.md) | - |
| Page Analysis | [page-analysis.md](reference/page-analysis.md) | `scripts/extract_pages.py` |
| Status Tracking | [status-tracking.md](reference/status-tracking.md) | `scripts/update_status.py`, `templates/homework-grading-status.yaml` |
| PDF Creation | [pdf-creation.md](reference/pdf-creation.md) | `scripts/create_student_pdfs.py` |
| Spreadsheet | [spreadsheet-update.md](reference/spreadsheet-update.md) | - |
| Verification | [verification.md](reference/verification.md) | - |
| Troubleshooting | [troubleshooting.md](reference/troubleshooting.md) | - |

## Required Skills Integration

**Always invoke these skills:**
```
Skill: document-skills:xlsx  # For spreadsheet operations
Skill: document-skills:pdf   # For PDF manipulation
```

## Critical Rules

### Phase 0 Rules (BEFORE ANYTHING ELSE)

1. **Create tracking file FIRST** - Before extracting PNGs or reading any pages
2. **Calculate batch plan upfront** - `ceil(total_pages / 99)` = number of sessions
3. **Display plan to user** - "150 pages = 2 sessions (99 + 51)"
4. **Get user confirmation** - Don't proceed without approval

### Page Analysis Rules

1. **One page at a time** - Use Read tool on each page image individually
2. **Name field location** - Look at TOP of worksheet ("Name:" or "Student:")
3. **Save to tracking file after EACH page** - Enables crash recovery and resume
4. **99-image limit per session** - Stop and inform user when limit reached

### Verification Rules

1. **Never skip verification** - Open EACH student PDF and confirm
2. **User must resolve uncertain pages** - Don't create PDFs with Unknown assignments
3. **Cross-check spreadsheet** - X marks must match PDFs created

## Red Flags - STOP and Review

If you notice ANY of these, stop and investigate:

| Red Flag | What's Wrong | Action |
|----------|-------------|--------|
| No tracking file yet | Starting analysis without Phase 0 | Create tracking file FIRST with batch plan |
| No batch plan shown | User doesn't know session count | Display plan, get confirmation |
| Batching pages | Reading multiple pages at once | Read ONE page per Read call |
| Skipping verification | Not opening created PDFs | Verify EACH PDF |
| Ignoring uncertain pages | Creating PDFs with Unknown | User must confirm names first |
| Not saving to tracking file | Only saving at end | Save after EACH page |
| Assuming page order | "Pages 1-10 are Student A" | Read name on EVERY page |

## Confidence Levels

| Level | Meaning | Action |
|-------|---------|--------|
| high | Name clear, exact roster match | Proceed |
| medium | Name readable, fuzzy match | Proceed with note |
| low | Name hard to read, best guess | Flag for user review |
| unknown | Cannot read name | MUST get user input |

## Session Resume

Claude has a 99-image limit per session. The tracking file manages this:

```
Phase 0:  Create tracking file, show batch plan:
          "150 pages = 2 sessions (99 + 51)"
          User confirms.

Session 1: Analyze pages 0-98, save each to tracking file
           At page 98: "Session limit reached. Resume in new session."

Session 2: Detect tracking file, resume from page 99
           Analyze pages 99-149
           All pages done → proceed to PDF creation
```

Tracking file location: `{output_folder}/homework-grading-status.yaml`

## Output Structure

```
{output_folder}/
├── homework-grading-status.yaml (workflow state)
├── Student Individual Files/
│   ├── {Student1}.pdf
│   ├── {Student2}.pdf
│   └── ...
└── {completion_spreadsheet} (updated)
```

## Common Mistakes

| Mistake | Why It Fails | Correct Approach |
|---------|-------------|------------------|
| Skipping Phase 0 | No batch plan, can't resume properly | Create tracking file FIRST |
| Not showing batch plan | User surprised by multi-session work | Display plan, get confirmation |
| Reading multiple pages at once | Can't accurately identify names | One page per Read call |
| Not checking Name field specifically | Other text confuses matching | Focus on "Name:" at top |
| Skipping PDF verification | Wrong pages get included | Open and check each PDF |
| Forcing through Unknown pages | Creates unusable output | Get user confirmation |
| Not using xlsx skill | Spreadsheet corruption | Always invoke xlsx skill first |

## Prerequisites

```bash
pip install PyMuPDF pandas openpyxl pyyaml filelock
```
