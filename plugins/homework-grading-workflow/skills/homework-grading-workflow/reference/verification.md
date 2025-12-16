# Verification - Detailed Instructions

## Overview

Verification ensures accuracy before finalizing the workflow. **DO NOT SKIP.**

## Verification Checklist

```
PDF Verification:
□ Each student PDF exists
□ Each PDF contains only that student's pages
□ Page counts match status file
□ No pages from other students mixed in

Spreadsheet Verification:
□ New assignment column added correctly
□ Column header matches assignment name
□ X marks match students with PDFs
□ Empty cells for students without submissions
□ Total formula updated and calculating
□ Existing columns preserved

Completeness Check:
□ All roster students accounted for
□ No duplicate PDFs
□ Unknown pages flagged for review
```

## Step 1: Verify Student PDFs

For EACH student PDF created:

```python
import fitz

output_dir = f"{output_folder}/Student Individual Files"

for student, data in students.items():
    pdf_path = f"{output_dir}/{student}.pdf"

    # Check file exists
    if not os.path.exists(pdf_path):
        print(f"❌ Missing: {student}.pdf")
        continue

    # Open and verify pages
    doc = fitz.open(pdf_path)
    expected_pages = len(data['pages'])
    actual_pages = len(doc)

    if actual_pages != expected_pages:
        print(f"⚠️ {student}.pdf: Expected {expected_pages} pages, found {actual_pages}")
    else:
        print(f"✓ {student}.pdf: {actual_pages} pages OK")

    doc.close()
```

## Step 2: Visual Spot Check

For at least 3 random student PDFs:
1. Open PDF using Read tool
2. Look at Name field on each page
3. Confirm name matches filename
4. Report any mismatches

## Step 3: Verify Spreadsheet

```python
from openpyxl import load_workbook

wb = load_workbook(completion_spreadsheet)
ws = wb[period]

# Find new column
new_col = None
for col in range(3, ws.max_column):
    if ws.cell(row=1, column=col).value == assignment_name:
        new_col = col
        break

if new_col is None:
    print("❌ New assignment column not found")
else:
    print(f"✓ Assignment column found at column {new_col}")

# Count submissions
x_count = sum(
    1 for row in range(2, ws.max_row + 1)
    if ws.cell(row=row, column=new_col).value == 'X'
)
pdf_count = len([s for s in students if students[s]['pages']])

if x_count == pdf_count:
    print(f"✓ X marks ({x_count}) match PDF count ({pdf_count})")
else:
    print(f"⚠️ Mismatch: {x_count} X marks vs {pdf_count} PDFs")
```

## Step 4: Cross-Reference Check

Create verification report:

```
Verification Report
==================

Students with submissions: {N}
Students without submissions: {M}
Total roster students: {N + M}

PDFs created: {pdf_count}
X marks in spreadsheet: {x_count}

Unknown pages: {unknown_count}
Low confidence pages: {low_conf_count}

Status: ✓ VERIFIED / ⚠️ NEEDS REVIEW
```

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing PDF | Student marked Unknown | Review page, assign to student |
| Extra X mark | Name in roster but no pages | Check page analysis for missed pages |
| Wrong page in PDF | Misread name | Re-analyze that page |
| Formula error | Column insertion issue | Manually fix formula range |

## Final Cleanup

After verification passes:

```bash
# Remove temporary page images
rm -rf {output_folder}/pages/

# Keep:
# - Original PDF (backup)
# - Student Individual Files/
# - Updated completion spreadsheet
# - homework-grading-status.yaml (for records)
```
