# Status Tracking - Schema and Usage

## Overview

The tracking file (`homework-grading-status.yaml`) persists progress across sessions. Claude has a **99-image limit per session**, so this file enables resume.

**CRITICAL**: Create this file BEFORE extracting PNGs or analyzing pages. Display the batch plan to user first.

## Session Limit

Claude can read a maximum of **99 images per session**. For a 150-page PDF, you need 2 sessions.

## Status File Schema

```yaml
# Homework Grading Status Tracking
# This file persists progress across sessions (Claude has 99 read limit)
# Resume workflow by running homework grading with same period

generated: '2025-12-16T06:30:00'
homework_pdf: /path/to/Homework-P4.pdf
roster_file: /path/to/Student-Master-List.xlsx
period: Period 4
output_folder: /path/to/output
completion_spreadsheet: /path/to/Homework-Completion-List.xlsx

workflow_status: init  # init | analyzing | verification | creating_pdfs | updating_spreadsheet | verifying | complete
total_pages: 121
last_analyzed_page: -1  # -1 means not started
pages_remaining: 121

# Page-by-page tracking
pages:
  0:
    status: analyzed
    raw_name: "Giovanni Figueroa"
    matched_student: "Giovanni"
    assignment: "Understanding Variables in Science Experiments"
    confidence: high
  1:
    status: analyzed
    raw_name: "Dami"
    matched_student: "Oluwadamilola"
    assignment: "Understanding Variables in Science Experiments"
    confidence: medium
  # ... more pages

# Student consolidation (built after all pages analyzed)
students: {}

# Pages needing user verification
uncertain_pages: []

# Assignments found
assignments_found:
  - Understanding Variables in Science Experiments
  - Identifying Variables
```

## Workflow Status Values

| Status | Description |
|--------|-------------|
| init | Gathering inputs, creating tracking file |
| analyzing | Reading pages, extracting names |
| verification | User reviewing uncertain pages |
| creating_pdfs | Generating individual student PDFs |
| updating_spreadsheet | Updating completion tracker |
| verifying | Final verification of outputs |
| complete | Workflow finished |

## Page Status Values

| Status | Description |
|--------|-------------|
| pending | Not yet analyzed |
| analyzed | Page read, name extracted |
| verified | User confirmed the student |
| skipped | User chose to skip this page |

## Confidence Levels

| Confidence | Criteria | Action |
|------------|----------|--------|
| high | Name clearly legible, exact roster match | Proceed automatically |
| medium | Name readable, fuzzy match found | Proceed with note |
| low | Name hard to read, best guess | Flag for user review |
| unknown | Cannot read name at all | MUST get user input |

## Creating the Tracking File

Before any page analysis:

```python
from scripts.update_status import create_tracking_file, display_batch_plan

# 1. Count pages first
import fitz
doc = fitz.open(homework_pdf)
total_pages = len(doc)
doc.close()

# 2. Show batch plan to user
print(display_batch_plan(total_pages))
# User must confirm before proceeding

# 3. Create tracking file
status, status_file = create_tracking_file(
    homework_pdf=homework_pdf,
    roster_file=roster_file,
    period=period,
    output_folder=output_folder,
    completion_spreadsheet=completion_spreadsheet,
    total_pages=total_pages
)
```

## Batch Plan Display

For a 150-page PDF:

```
📋 BATCH PLAN
Total pages: 150
Max per session: 99
Sessions needed: 2

  Session 1: pages 0-98 (99 pages)
  Session 2: pages 99-149 (51 pages)

⚠️ This will require 2 Claude session(s) to complete.
Continue? (User must confirm)
```

## Resuming a Session

When workflow resumes, check tracking file:

```python
from scripts.update_status import load_tracking_file, get_resume_info

status, status_file = load_tracking_file(output_folder)
if status:
    next_page, pages_remaining = get_resume_info(status)
    if next_page is not None:
        print(f"📂 Resuming from page {next_page} ({pages_remaining} remaining)")
```

## Updating Progress

After each page, update tracking file immediately:

```python
from scripts.update_status import update_page

page_data = {
    'raw_name': raw_name,
    'matched_student': matched_student,
    'assignment': assignment,
    'confidence': confidence
}

update_page(status, status_file, page_num, page_data)
# Status file is saved automatically
```

**SAVE AFTER EVERY PAGE** - This enables crash recovery.

## Session Limit Check

Monitor image count during analysis:

```python
from scripts.update_status import check_session_limit

images_read = 0
for page_num in range(start_page, total_pages):
    # Read page image
    images_read += 1

    # Check limit
    limit_reached, message = check_session_limit(images_read, status)
    if limit_reached:
        print(message)
        break  # Stop, user must start new session

    # Analyze page...
    update_page(status, status_file, page_num, page_data)
```

## Session Limit Message

When limit is reached:

```
⚠️ SESSION LIMIT REACHED (99 images)

Progress saved to tracking file.
Analyzed pages 0-98
Pages remaining: 51

To continue:
1. Start a new Claude session
2. Run homework grading workflow again
3. Will resume from page 99
```
