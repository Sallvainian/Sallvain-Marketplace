# Spreadsheet Update - Detailed Instructions

## Overview

Updates the existing homework completion spreadsheet with a new assignment column.

## Prerequisites

**INVOKE XLSX SKILL FIRST**:
```
Skill: document-skills:xlsx
```

```python
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
```

## Expected Spreadsheet Format

```
| # | Student Name | Assignment1 | Assignment2 | ... | Total |
|---|--------------|-------------|-------------|-----|-------|
| 1 | Alice        | X           | X           | ... | 2     |
| 2 | Bob          | X           |             | ... | 1     |
```

- Column A: Student number
- Column B: Student name
- Columns C+: Assignments (marked with 'X')
- Last column: Total formula counting X marks

## Step 1: Open Spreadsheet

```python
wb = load_workbook(completion_spreadsheet)
ws = wb[period]  # e.g., "Period 4"
```

## Step 2: Find Total Column

```python
total_col = None
for col in range(ws.max_column, 0, -1):
    cell_value = ws.cell(row=1, column=col).value
    if cell_value and 'Total' in str(cell_value):
        total_col = col
        break

if total_col is None:
    raise ValueError("Could not find 'Total' column")
```

## Step 3: Insert New Assignment Column

```python
# Insert column at Total's position (pushes Total right)
new_col = total_col
ws.insert_cols(new_col)

# Set header
assignment_name = "Assignment Name"  # Use actual assignment name
ws.cell(row=1, column=new_col, value=assignment_name)
ws.cell(row=1, column=new_col).font = Font(bold=True)
ws.cell(row=1, column=new_col).alignment = Alignment(horizontal='center')
```

## Step 4: Mark Submissions

```python
# Define fills
green_fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
red_fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')

# students dict contains names with submissions
for row in range(2, ws.max_row + 1):
    student_name = ws.cell(row=row, column=2).value  # Column B
    if student_name:
        has_submission = student_name in students
        cell = ws.cell(row=row, column=new_col)
        cell.value = 'X' if has_submission else ''
        cell.fill = green_fill if has_submission else red_fill
        cell.alignment = Alignment(horizontal='center')
```

## Step 5: Update Total Formula

```python
# Total column shifted right by 1
new_total_col = total_col + 1
last_data_col = new_total_col - 1
last_col_letter = get_column_letter(last_data_col)

for row in range(2, ws.max_row + 1):
    formula = f'=COUNTIF(C{row}:{last_col_letter}{row},"X")'
    ws.cell(row=row, column=new_total_col).value = formula
```

## Step 6: Save

```python
wb.save(completion_spreadsheet)
print(f"Updated: {completion_spreadsheet}")
```

## Verification

After saving:
1. Open spreadsheet
2. Verify new column exists with correct header
3. Check X marks match students with PDFs
4. Verify Total formulas calculate correctly
5. Confirm existing data preserved
