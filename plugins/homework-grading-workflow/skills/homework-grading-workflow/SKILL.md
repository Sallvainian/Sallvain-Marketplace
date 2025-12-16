---
name: Processing Homework Submissions
description: Processes scanned homework PDFs by extracting student names using vision, matching against roster, creating individual student PDFs, and updating completion spreadsheets. Use when processing homework scans, organizing submissions by student, grading assignments, or tracking homework completion.
---

# Processing Homework Submissions

Automates processing of scanned student homework through a multi-phase verification workflow.

## Contents

- [Quick Start](#quick-start)
- [Required Inputs](#required-inputs)
- [Workflow Overview](#workflow-overview)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Page Analysis](#phase-2-page-analysis)
- [Phase 3: PDF Creation](#phase-3-pdf-creation)
- [Phase 4: Update Spreadsheet](#phase-4-update-spreadsheet)
- [Phase 5: Verification](#phase-5-verification)
- [Troubleshooting](#troubleshooting)

## Critical Success Factors

Three things ensure accuracy:

1. **Read EVERY page individually** - Never batch pages. Analyze each with vision.
2. **Focus on the Name field** - Look at TOP of worksheet where "Name:" appears.
3. **Verify after PDF creation** - Open EACH student PDF and confirm pages match.

## Quick Start

```
1. Gather: homework PDF, roster Excel, completion spreadsheet
2. Invoke document-skills:xlsx before spreadsheet operations
3. Extract PDF pages as images
4. Analyze each page with vision (read Name field)
5. Create individual student PDFs
6. Update completion spreadsheet
7. Verify all outputs
```

## Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| `homework_pdf` | Scanned homework PDF | `Homework-1.pdf` |
| `roster_file` | Student roster Excel | `Student-Master-List.xlsx` |
| `period` | Class period (sheet name) | `Period 4` |
| `output_folder` | Output directory | `./P4/` |
| `completion_spreadsheet` | Homework tracker | `Homework-Completion-List.xlsx` |

## Skill Dependencies

**CRITICAL**: Invoke these skills before related operations:

| Skill | When to Invoke |
|-------|----------------|
| `document-skills:xlsx` | Before any spreadsheet operation |
| `document-skills:pdf` | Before PDF manipulation |

```
Skill: document-skills:xlsx
```

## Workflow Overview

| Phase | Description | Details |
|-------|-------------|---------|
| 1. Setup | Validate files, read roster | Below |
| 2. Page Analysis | Read each page with vision | [reference/page-analysis.md](reference/page-analysis.md) |
| 3. PDF Creation | Create student PDFs | [reference/pdf-creation.md](reference/pdf-creation.md) |
| 4. Spreadsheet | Update completion checklist | [reference/spreadsheet-update.md](reference/spreadsheet-update.md) |
| 5. Verification | Verify all outputs | [reference/verification.md](reference/verification.md) |

## Phase 1: Setup

### 1.1 Validate Required Files

Confirm all input files exist before proceeding.

### 1.2 Read Roster

**Invoke xlsx skill first**, then read the period sheet and extract student names into a list.

### 1.3 Extract PDF Pages

```bash
python scripts/extract_pages.py {homework_pdf} {output_folder}/pages/
```

Creates numbered images: `page_000.png`, `page_001.png`, etc.

### 1.4 Initialize Status File

Progress persists to `homework-grading-status.yaml` for crash recovery and session resumption.

See [reference/status-tracking.md](reference/status-tracking.md) for schema.

## Phase 2: Page Analysis

**THE KEY TO ACCURACY**: Read EVERY page individually with vision.

For each page:
1. Use Read tool to view `pages/page_NNN.png`
2. Focus on **"Name:" field** at the TOP
3. Read handwritten name carefully
4. Match to roster using fuzzy matching
5. Record with confidence level (high/medium/low/unknown)
6. Save status after EACH page

**Detailed instructions**: See [reference/page-analysis.md](reference/page-analysis.md)

### Processing Modes

| Mode | Use When | Description |
|------|----------|-------------|
| Sequential (default) | <50 pages | Process one at a time |
| Parallel | >50 pages | Dispatch subagents |

For parallel processing, see [reference/parallel-processing.md](reference/parallel-processing.md).

### Manual Verification

Before PDF creation, verify any pages with `confidence < high` or unreadable names. Display page image to user and confirm/correct assignment.

## Phase 3: PDF Creation

Group pages by student and create individual PDFs.

```bash
python scripts/create_student_pdfs.py {status_file} {homework_pdf} {output_folder}
```

**Detailed instructions**: See [reference/pdf-creation.md](reference/pdf-creation.md)

## Phase 4: Update Spreadsheet

**INVOKE XLSX SKILL FIRST**

1. Open existing completion spreadsheet
2. Insert new assignment column before "Total"
3. Mark submissions with 'X' (green fill) or blank (red fill)
4. Update Total formula

**Detailed instructions**: See [reference/spreadsheet-update.md](reference/spreadsheet-update.md)

## Phase 5: Verification

**DO NOT SKIP** - Verification catches errors.

```
Checklist:
□ Each student PDF contains only that student's pages
□ Page counts match expected
□ Spreadsheet column added correctly
□ X marks match created PDFs
□ Total formulas updated
```

**Detailed instructions**: See [reference/verification.md](reference/verification.md)

## Output Structure

```
{output_folder}/
├── {homework_pdf} (original, preserved)
├── Student Individual Files/
│   ├── StudentName1.pdf
│   ├── StudentName2.pdf
│   └── ...
├── pages/ (temporary, delete after verification)
└── homework-grading-status.yaml

{completion_spreadsheet} (updated in place)
```

## Accuracy Tips

| Tip | Why |
|-----|-----|
| Focus on Name field | Usually at top, labeled "Name:" or "Student:" |
| Read letter by letter | Helps with messy handwriting |
| Compare to roster | Pick closest match |
| Check consistency | Same student's writing looks similar |

### Fuzzy Matching

| Written | Roster Match | Reason |
|---------|--------------|--------|
| "Eliana Lugo" | Eliomar | Similar first name |
| "J. Smith" | James/Jeremy | Check other pages |
| Illegible | Unknown | Flag for manual review |

### Common Mistakes

- Assuming page order = student order
- Skipping pages
- Not verifying after PDF creation
- Mixing up similar names (James vs Jeremy)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Unreadable name | Set confidence to `unknown`, flag for manual review |
| Session limit reached | Progress saved automatically; resume by running again |
| Missing student | Include in checklist with empty cell, no PDF created |
| Duplicate names | Use last name or check period number |

**Detailed troubleshooting**: See [reference/troubleshooting.md](reference/troubleshooting.md)

## Prerequisites

```bash
pip install PyMuPDF pyyaml openpyxl filelock
```
