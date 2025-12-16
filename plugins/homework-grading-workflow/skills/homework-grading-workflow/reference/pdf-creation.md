# PDF Creation - Detailed Instructions

## Overview

Creates individual PDF files for each student by extracting and combining their pages from the source PDF.

## Prerequisites

```python
import fitz  # PyMuPDF
import yaml
import os
```

## Step 1: Load Status File

```python
with open(status_file, 'r') as f:
    status = yaml.safe_load(f)
```

## Step 2: Build Student Page Mapping

```python
students = {}
for page_num, page_data in status['pages'].items():
    student = page_data.get('matched_student', 'Unknown')
    if student == 'Unknown':
        continue  # Skip unassigned pages

    if student not in students:
        students[student] = {
            'pages': [],
            'assignments': set()
        }

    students[student]['pages'].append(int(page_num))
    students[student]['assignments'].add(page_data.get('assignment', 'Unknown'))
```

## Step 3: Create Output Directory

```python
output_dir = os.path.join(output_folder, 'Student Individual Files')
os.makedirs(output_dir, exist_ok=True)
```

## Step 4: Generate Student PDFs

```python
src_pdf = fitz.open(homework_pdf)

for student, data in students.items():
    if not data['pages']:
        continue

    # Create new PDF
    student_pdf = fitz.open()

    # Add pages in order
    for page_num in sorted(data['pages']):
        student_pdf.insert_pdf(src_pdf, from_page=page_num, to_page=page_num)

    # Save
    output_path = os.path.join(output_dir, f"{student}.pdf")
    student_pdf.save(output_path)
    student_pdf.close()

    print(f"Created: {student}.pdf ({len(data['pages'])} pages)")

src_pdf.close()
```

## Step 5: Handle Unknown Pages

Pages with `matched_student = 'Unknown'` are not included in any PDF. These require manual assignment before PDF creation.

```python
unknown_pages = [
    page_num for page_num, data in status['pages'].items()
    if data.get('matched_student') == 'Unknown'
]

if unknown_pages:
    print(f"⚠️ {len(unknown_pages)} pages not assigned to any student")
    print(f"Pages: {unknown_pages}")
```

## Output

```
Student Individual Files/
├── StudentA.pdf (3 pages)
├── StudentB.pdf (2 pages)
├── StudentC.pdf (2 pages)
└── ...
```

## Verification After Creation

After creating PDFs, verify each one:
1. Open with Read tool
2. Check all pages belong to named student
3. Confirm page count matches expected

See [verification.md](verification.md) for detailed verification steps.
