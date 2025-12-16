---
name: homework-grading-workflow
description: Process scanned homework PDFs by extracting student names from pages using vision, matching against a roster Excel file, grouping pages by student, creating individual PDFs per student, and generating completion checklists. Use when you have scanned homework submissions, need to organize homework by student, grade student work, or process a batch of student assignments from a PDF.
---

# Homework Grading Workflow

## Overview

This skill automates the processing of scanned student homework submissions through a multi-pass verification workflow that ensures accuracy.

## ⚠️ THE REAL ACCURACY FIX

**These three things are what made this workflow accurate:**

1. **Reading EVERY page individually** - Do NOT batch pages. Analyze each page one at a time with Claude's vision.
2. **Focusing on the Name field specifically** - Look at the TOP of each worksheet where "Name:" appears. Ignore other text.
3. **Verification phase after PDF creation** - Open EACH student PDF and confirm all pages belong to that student before finishing.

## Critical Skills Integration

**IMPORTANT**: This workflow uses these skills in conjunction:
- **xlsx skill**: For reading roster files and creating/updating completion checklists
- **pdf skill**: For extracting and creating PDF files
- **Vision (Read tool)**: For reading handwritten names from scanned pages

When processing spreadsheets, **always invoke the xlsx skill first** by calling:
```
Skill: document-skills:xlsx
```

## Workflow Phases

### Phase 1: Setup and Data Collection

#### Step 1.1: Identify Required Files
```
Required inputs:
├── Homework PDF (e.g., Homework-1.pdf) - scanned student submissions
└── Student roster (e.g., Student-Master-List.xlsx) - with period sheets (P1, P3, P4, P6, P7, P9)
```

#### Step 1.2: Read the Roster (USE XLSX SKILL)
**Invoke xlsx skill** to read the student roster:
```
1. Open Student-Master-List.xlsx
2. Read the sheet for the target period (e.g., "P9")
3. Extract all student names into a list
4. Note total student count for verification
```

Store roster as reference list:
```python
roster = ['Alexandler', 'Briana', 'Delilah', 'Eliomar', 'Elizabeth',
          'James', 'Jayvon', 'Jeremy', 'Keyla', 'Laila',
          'Logan', 'Maria', 'Markeeda', 'Nahyla', 'Rafiah']
```

### Phase 2: Page-by-Page Analysis (CRITICAL FOR ACCURACY)

#### Step 2.1: Extract PDF Pages as Images
```python
import fitz
import os

os.makedirs('pages', exist_ok=True)
doc = fitz.open('Homework-1.pdf')
total_pages = len(doc)
print(f"Total pages to analyze: {total_pages}")

for i in range(total_pages):
    page = doc[i]
    pix = page.get_pixmap(dpi=150)
    pix.save(f'pages/page_{i:03d}.png')
```

#### Step 2.2: Analyze EVERY Page Individually
**This is the most critical step for accuracy.**

For EACH page (0 to N-1):
1. Use Claude's Read tool to view the page image
2. Look at the **"Name:" field** at the TOP of the worksheet
3. Read the handwritten student name carefully
4. Identify the assignment type from the page header/title
5. Record in structured format

**Page Analysis Template:**
```
Page X:
- Raw name read: [exactly what you see written]
- Matched student: [roster match]
- Assignment: [assignment title from header]
- Confidence: [high/medium/low]
- Notes: [any issues]
```

#### Step 2.3: Build Page Mapping Data Structure
After analyzing ALL pages, create mapping:
```python
page_mapping = {
    0: {'student': 'Keyla', 'assignment': 'Identifying Variables', 'page_of': 1},
    1: {'student': 'Keyla', 'assignment': 'Identifying Variables', 'page_of': 2},
    2: {'student': 'Briana', 'assignment': 'Identifying Variables', 'page_of': 1},
    # ... continue for ALL pages
}

# Then consolidate by student:
students = {}
for page_num, info in page_mapping.items():
    student = info['student']
    if student not in students:
        students[student] = {'pages': [], 'assignments': set()}
    students[student]['pages'].append(page_num)
    students[student]['assignments'].add(info['assignment'])
```

### Phase 3: Identify Assignment Types

Scan through page_mapping to identify unique assignments:
```python
assignments_found = set()
for page_num, info in page_mapping.items():
    assignments_found.add(info['assignment'])

print(f"Assignments found: {assignments_found}")
```

Common assignment patterns:
| Assignment | Pages | Identifier |
|------------|-------|------------|
| Identifying Variables | 2 | Title at top |
| Changes in Kinetic Energy | 1 | Blue/colored page |
| Investigation Planning Guide | 2 | "Planning Guide" header |
| Investigating Force Interaction | 2 | "Force Interaction" header |
| Lesson 5: Variables | 1 | "Lesson 5" header |

### Phase 4: Create Individual Student PDFs

#### Step 4.1: Create Output Directory
```python
import os
os.makedirs('Student Individual Files', exist_ok=True)
```

#### Step 4.2: Generate PDFs
```python
import fitz

src = fitz.open('Homework-1.pdf')

for student, data in students.items():
    if data['pages']:  # Only if student has submissions
        output = fitz.open()
        for page_num in sorted(data['pages']):
            output.insert_pdf(src, from_page=page_num, to_page=page_num)
        output.save(f'Student Individual Files/{student}.pdf')
        output.close()
        print(f"Created: {student}.pdf ({len(data['pages'])} pages)")

src.close()
```

### Phase 5: Create/Update Completion Checklist (USE XLSX SKILL)

**CRITICAL: Invoke the xlsx skill** for spreadsheet operations:
```
Skill: document-skills:xlsx
```

#### Step 5.1: Build Checklist Data
```python
checklist_data = []
for student in roster:
    row = {'Student': student}
    if student in students:
        for assignment in assignments_found:
            row[assignment] = 'X' if assignment in students[student]['assignments'] else ''
        row['Total'] = len(students[student]['assignments'])
    else:
        for assignment in assignments_found:
            row[assignment] = ''
        row['Total'] = 0
    checklist_data.append(row)
```

#### Step 5.2: Create/Update Excel File
Using xlsx skill, create workbook with:
- One sheet per period (P1, P3, P4, P6, P7, P9)
- Columns: Student Name | Assignment1 | Assignment2 | ... | Total
- Formatting:
  - Header row bold
  - Green fill for submitted (X)
  - Red fill for missing (empty)
  - Auto-fit column widths

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active
ws.title = "P9"  # or appropriate period

# Headers
headers = ['Student'] + list(assignments_found) + ['Total']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal='center')

# Data rows
green_fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
red_fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')

for row_num, data in enumerate(checklist_data, 2):
    ws.cell(row=row_num, column=1, value=data['Student'])
    for col_num, assignment in enumerate(assignments_found, 2):
        cell = ws.cell(row=row_num, column=col_num, value=data.get(assignment, ''))
        if data.get(assignment) == 'X':
            cell.fill = green_fill
        else:
            cell.fill = red_fill
    ws.cell(row=row_num, column=len(headers), value=data['Total'])

wb.save('Homework-Completion-List.xlsx')
```

### Phase 6: Verification (CRITICAL FOR ACCURACY)

**DO NOT SKIP THIS PHASE**

#### Step 6.1: Verify Each Student PDF
For EACH student PDF created:
1. Open the PDF file using Read tool
2. Check that ALL pages belong to that student
3. Verify page count matches expected
4. Close before opening next file

```
Verification checklist:
□ Student name on all pages matches filename
□ Page count matches mapping
□ No pages from other students
□ Assignment types are correctly identified
```

#### Step 6.2: Cross-Reference with Checklist
- Verify checklist matches actual PDFs created
- Confirm students with no submissions have empty rows
- Check total counts are accurate

### Phase 7: Cleanup

After verification is complete:
```bash
rm -rf pages/  # Remove extracted images
```

Keep:
- Original PDF (backup)
- Student Individual Files/ folder
- Homework-Completion-List.xlsx

## Output Structure

```
P9/
├── Homework-1.pdf (original, keep as backup)
├── Student Individual Files/
│   ├── Alexandler.pdf
│   ├── Briana.pdf
│   ├── Delilah.pdf
│   ├── Eliomar.pdf
│   ├── Elizabeth.pdf
│   ├── James.pdf
│   ├── Jayvon.pdf
│   ├── Jeremy.pdf
│   ├── Keyla.pdf
│   ├── Laila.pdf
│   ├── Maria.pdf
│   ├── Markeeda.pdf
│   └── Nahyla.pdf
└── Homework-Completion-List.xlsx
```

## Accuracy Tips

### Reading Handwritten Names
1. **Focus on the Name field** - Usually top of page, labeled "Name:" or "Student:"
2. **Read letter by letter** for messy handwriting
3. **Compare to roster** - Pick closest match
4. **Check consistency** - Same student's handwriting should look similar across pages
5. **Look for full names** - First + Last name provides better matching

### Fuzzy Matching Rules
| Written | Roster Match | Reason |
|---------|--------------|--------|
| "Eliana Lugo" | Eliomar | Similar first name |
| "J. Smith" | James/Jeremy | Check other pages |
| Illegible | Unknown | Flag for manual review |

### Common Mistakes to Avoid
- ❌ Assuming page order = student order
- ❌ Skipping pages
- ❌ Not verifying after PDF creation
- ❌ Mixing up similar names (James vs Jeremy)
- ✅ Read EVERY page individually
- ✅ Verify EVERY student PDF
- ✅ Cross-check with roster

## Error Handling

### Unreadable Names
```python
unknown_pages = []  # Collect pages that can't be identified
# After processing, report:
if unknown_pages:
    print(f"Manual review needed for pages: {unknown_pages}")
```

### Missing Students
Students on roster with no submissions:
- Include in checklist with empty columns
- Do NOT create empty PDF files

### Duplicate Names
If roster has duplicate first names:
- Use last name to differentiate
- Check period number on worksheet

## When to Use This Skill

Trigger phrases:
- "Process this homework PDF"
- "Organize homework by student"
- "Grade these submissions"
- "Sort student assignments"
- "Create individual student files from this PDF"
- "Check who submitted homework"
- "Update homework checklist"
- "Which students are missing assignments"

## Prerequisites

Required Python packages:
```bash
pip install PyMuPDF pandas openpyxl
```

## Related Skills
- **xlsx**: For spreadsheet operations (ALWAYS use for checklist)
- **pdf**: For PDF manipulation
