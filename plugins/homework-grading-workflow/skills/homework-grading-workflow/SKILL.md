---
name: homework-grading-workflow
description: Process scanned homework PDFs by extracting student names from pages using vision, matching against a roster Excel file, grouping pages by student, creating individual PDFs per student, and generating completion checklists. Use when you have scanned homework submissions, need to organize homework by student, grade student work, or process a batch of student assignments from a PDF.
---

# Homework Grading Workflow

## Overview

This skill automates the processing of scanned student homework submissions by:
1. Extracting pages from PDFs as images
2. Using Claude's vision to identify student names from handwritten submissions
3. Matching names to a student roster (Excel file with period sheets)
4. Grouping pages by student
5. Creating individual PDFs per student in a "Student Individual Files" subfolder
6. Generating a homework completion checklist Excel file

## When to Use This Skill

Trigger phrases:
- "Process this homework PDF"
- "Organize homework by student"
- "Grade these submissions"
- "Sort student assignments"
- "Create individual student files from this PDF"
- "Check who submitted homework"

## Prerequisites

Required Python packages:
```bash
pip install PyMuPDF pandas openpyxl
```

## Workflow Steps

### Step 1: Identify the Files

You need:
- A PDF file containing scanned homework (multiple students, multiple pages)
- An Excel roster file (Student-Master-List.xlsx) with sheets for each period (P1, P3, P4, P6, P7, P9)

### Step 2: Extract PDF Pages as Images

```python
import fitz

doc = fitz.open('Homework-1.pdf')
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=150)
    pix.save(f'pages/page_{i+1:02d}.png')
```

### Step 3: Read Each Page Using Vision

Use Claude's Read tool to view each page image. Look for:
- The "Name:" field at the top of each worksheet
- Student's handwritten name
- Period number if visible
- Date if visible

### Step 4: Match Names to Roster

Compare extracted names to the period roster:
- Handle spelling variations (e.g., "Eliana" vs "Eliomar")
- Match partial names (first name or last name)
- Use fuzzy matching for messy handwriting

### Step 5: Create Student Mapping

Build a dictionary mapping each student to their page numbers:
```python
students = {
    'StudentName': [0, 1, 5, 6],  # 0-indexed page numbers
    ...
}
```

### Step 6: Generate Individual PDFs

```python
import fitz

src = fitz.open('Homework-1.pdf')
for name, pages in students.items():
    if pages:
        output = fitz.open()
        for page_num in sorted(pages):
            output.insert_pdf(src, from_page=page_num, to_page=page_num)
        output.save(f'Student Individual Files/{name}.pdf')
        output.close()
```

### Step 7: Create Completion Checklist

Generate an Excel file with:
- Student names from roster
- Columns for each assignment found
- Checkmarks (X) or empty cells for submission status
- Total count per student

## Assignment Types to Look For

Common physics/science assignments:
- Identifying Variables (2 pages)
- Changes in Kinetic Energy (1 blue page)
- Investigation Planning Guide (2 pages)
- Investigating Force Interaction (2 pages)
- Lesson 5: Independent, Dependent, and Controlled Variables (1 page)

## Output Structure

```
P9/
├── Homework-1.pdf (original, keep as backup)
├── pages/ (extracted images, can delete after)
├── Student Individual Files/
│   ├── Alexandler.pdf
│   ├── Briana.pdf
│   ├── ...
│   └── Rafiah.pdf
└── Homework-Completion-List.xlsx
```

## Handling Edge Cases

### Unreadable Names
- Mark as "Unknown" with page numbers
- Ask user to manually review

### Multiple Assignment Types
- Identify assignment by:
  - Page header/title
  - Color (blue pages = Kinetic Energy)
  - Format/structure

### Missing Students
- List students from roster with no submissions
- Show in completion checklist as empty row

## Tips for Accuracy

1. Read the name field carefully - look at top of page
2. Compare handwriting style across pages from same student
3. Check period number matches the roster being used
4. Look for full name (first + last) when available
5. When uncertain, list similar roster names and best guess

## Cleanup

After verification:
```bash
rm -rf pages/  # Remove extracted images
```

Keep:
- Original PDF (backup)
- Student Individual Files folder
- Completion checklist
