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
├── Student roster (e.g., Student-Master-List.xlsx) - with period sheets (Period 1, Period 3, Period 4, Period 6, Period 7, Period 9)
└── Completion spreadsheet (e.g., Homework-Completion-List.xlsx) - existing homework tracker to update
```

**Completion Spreadsheet Structure:**
```
Expected format:
- Column A: # (student number)
- Column B: Student Name
- Columns C+: Assignment names as headers
- Last column: Total (formula counting X marks)
- Mark submissions with 'X'
```

#### Step 1.2: Read the Roster (USE XLSX SKILL)
**Invoke xlsx skill** to read the student roster:
```
1. Open Student-Master-List.xlsx
2. Read the sheet for the target period (e.g., "Period 9")
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

**IMPORTANT**: Claude has a 99 image read limit per session. This workflow uses a status file to persist progress and allow resuming across sessions.

#### Step 2.0: Initialize or Resume Status Tracking
```python
import yaml
import os
from datetime import datetime

status_file = '{output_folder}/homework-grading-status.yaml'

# Check for existing status file (resume mode)
if os.path.exists(status_file):
    with open(status_file, 'r') as f:
        status = yaml.safe_load(f)
    last_page = status.get('last_analyzed_page', -1)
    print(f"📂 Resuming from page {last_page + 1}")
else:
    # Create new status file
    status = {
        'generated': datetime.now().isoformat(),
        'workflow_status': 'analyzing',
        'total_pages': 0,
        'last_analyzed_page': -1,
        'pages': {},
        'students': {},
        'uncertain_pages': [],
        'assignments_found': []
    }
    print("📝 Created new status tracking file")
```

#### Step 2.1: Extract PDF Pages as Images
```python
import fitz

os.makedirs('pages', exist_ok=True)
doc = fitz.open('Homework-1.pdf')
total_pages = len(doc)
status['total_pages'] = total_pages
print(f"Total pages to analyze: {total_pages}")

# Extract pages (skip if already extracted)
for i in range(total_pages):
    page_path = f'pages/page_{i:03d}.png'
    if not os.path.exists(page_path):
        page = doc[i]
        pix = page.get_pixmap(dpi=150)
        pix.save(page_path)

# Save status
with open(status_file, 'w') as f:
    yaml.dump(status, f, default_flow_style=False)
```

#### Step 2.1.5: Choose Processing Mode

```
📊 **Processing Mode**

Total pages to analyze: {total_pages}

[S] Sequential - Process pages one at a time (slower, but you see each page)
[P] Parallel - Dispatch subagents to process simultaneously (faster)

Recommended: Parallel for >20 pages
```

**If Parallel mode selected:**

##### Dispatch Subagents in Parallel
```python
num_subagents = min(4, (total_pages + 24) // 25)  # ~25 pages per subagent
pages_per_agent = total_pages // num_subagents
```

Use the Task tool to dispatch multiple subagents in a SINGLE message:
- Each subagent processes a range of pages
- All subagents update the shared status file with thread-safe locking
- Report completion when done

**Subagent prompt template:**
```
You are a page-reader subagent. Your task:
1. Process pages {start_page} to {end_page} from: {pages_folder}
2. For each page, read with vision and extract:
   - Student name (from 'Name:' field at top)
   - Assignment name (from header)
   - Confidence level (high/medium/low/unknown)
3. Update status file with thread-safe locking (fcntl): {status_file}
4. Roster for matching: {roster}
```

##### Validate After Subagents Complete
```
🔍 **Subagent Validation Check**

1. All pages have entries (0 to total_pages-1)
2. No duplicate student assignments for same page
3. Roster names used correctly
4. Red flags:
   - Same student on >50% of pages
   - Student not in roster
   - Too many "UNKNOWN" (>20%)
```

---

**If Sequential mode selected (or resuming):**

#### Step 2.2: Analyze EVERY Page Individually (with Resume Support)
**This is the most critical step for accuracy.**

**RESUME LOGIC**: Skip pages already in status file, start from `last_analyzed_page + 1`

```python
start_page = status['last_analyzed_page'] + 1
if start_page > 0:
    print(f"⏩ Skipping pages 0-{start_page - 1} (already analyzed)")
```

For EACH page (starting from `start_page`):
1. Use Claude's Read tool to view the page image
2. Look at the **"Name:" field** at the TOP of the worksheet
3. Read the handwritten student name carefully
4. Identify the assignment type from the page header/title
5. Record in status file IMMEDIATELY after each page
6. Save status file after EVERY page (crash recovery)

**Page Analysis Template:**
```
Page X:
- Raw name read: [exactly what you see written]
- Matched student: [roster match]
- Assignment: [assignment title from header]
- Confidence: [high/medium/low]
- Notes: [any issues]
```

**After EACH page, update and save status:**
```python
status['pages'][page_num] = {
    'status': 'analyzed',
    'raw_name': raw_name,
    'matched_student': matched_student,
    'assignment': assignment,
    'confidence': confidence
}
status['last_analyzed_page'] = page_num

# Save immediately (crash recovery)
with open(status_file, 'w') as f:
    yaml.dump(status, f, default_flow_style=False)
```

**If 99 read limit reached:**
```
⚠️ Session Limit Reached

Analyzed {N} pages this session (99 limit).
Progress saved to: {status_file}

To continue:
1. Start a new Claude session
2. Run the homework grading workflow again
3. Workflow will resume from page {N+1}
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

### Phase 3.5: User Verification of Uncertain Pages

**CRITICAL**: Before creating PDFs, the user MUST verify any pages with low confidence or unreadable names.

If there are pages with confidence < high OR pages where the name could not be read:

```
⚠️ **Manual Verification Required**

The following pages need your review:

**Low Confidence Matches:**
| Page | Raw Name Read | Best Match | Confidence |
|------|---------------|------------|------------|
| {page_num} | "{raw_name}" | {matched_student} | low |

**Unreadable Names:**
| Page | Notes |
|------|-------|
| {page_num} | Could not make out name |

Please verify or correct each entry.
```

For each uncertain page:
1. Display the page image to the user
2. Ask: "Who does this page belong to? (or type 'skip' to exclude)"
3. Update the page_mapping with user's correction
4. Continue to next uncertain page

Only proceed to PDF creation after ALL uncertain pages are resolved.

```python
# Collect pages needing review
uncertain_pages = []
for page_num, info in page_mapping.items():
    if info.get('confidence') in ['low', 'unknown'] or info.get('student') == 'Unknown':
        uncertain_pages.append((page_num, info))

if uncertain_pages:
    print(f"⚠️ {len(uncertain_pages)} pages need manual verification")
    for page_num, info in uncertain_pages:
        # Show page image and ask user to confirm/correct
        user_response = ask_user(f"Page {page_num}: Read as '{info.get('raw_name')}', matched to '{info.get('student')}'. Correct?")
        if user_response != 'skip':
            page_mapping[page_num]['student'] = user_response
            page_mapping[page_num]['confidence'] = 'user_verified'
```

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

### Phase 5: Update Existing Completion Spreadsheet (USE XLSX SKILL)

**CRITICAL: Invoke the xlsx skill** for spreadsheet operations:
```
Skill: document-skills:xlsx
```

#### Step 5.1: Open Existing Spreadsheet
```python
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Open existing spreadsheet
wb = load_workbook('{completion_spreadsheet}')
ws = wb['{period}']  # e.g., "Period 9"
```

#### Step 5.2: Find and Insert New Assignment Column
```python
# Find the Total column (last column with data in row 1)
total_col = None
for col in range(ws.max_column, 0, -1):
    if ws.cell(row=1, column=col).value == 'Total':
        total_col = col
        break

# Insert new assignment column before Total
new_col = total_col  # Insert at Total's position, pushing Total right
ws.insert_cols(new_col)

# Set assignment header
assignment_name = list(assignments_found)[0] if len(assignments_found) == 1 else "Assignment"
ws.cell(row=1, column=new_col, value=assignment_name)
ws.cell(row=1, column=new_col).font = Font(bold=True)
ws.cell(row=1, column=new_col).alignment = Alignment(horizontal='center')
```

#### Step 5.3: Mark Submissions
```python
green_fill = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')
red_fill = PatternFill(start_color='FFB6C1', end_color='FFB6C1', fill_type='solid')

for row in range(2, ws.max_row + 1):
    student_name = ws.cell(row=row, column=2).value  # Column B = Student Name
    if student_name:
        has_submission = student_name in students
        cell = ws.cell(row=row, column=new_col)
        cell.value = 'X' if has_submission else ''
        cell.fill = green_fill if has_submission else red_fill
        cell.alignment = Alignment(horizontal='center')
```

#### Step 5.4: Update Total Formula
```python
# Update Total formula in the new Total column position (shifted right by 1)
new_total_col = total_col + 1
new_total_letter = get_column_letter(new_total_col - 1)
for row in range(2, ws.max_row + 1):
    # Count all X marks from column C to the column before Total
    ws.cell(row=row, column=new_total_col).value = f'=COUNTIF(C{row}:{new_total_letter}{row},"X")'

wb.save('{completion_spreadsheet}')
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

#### Step 6.2: Cross-Reference with Spreadsheet
- Verify new assignment column was added correctly
- Confirm X marks match students with PDFs
- Check Total formulas updated
- Verify existing columns preserved

### Phase 7: Cleanup

After verification is complete:
```bash
rm -rf pages/  # Remove extracted images
```

Keep:
- Original PDF (backup)
- Student Individual Files/ folder
- {completion_spreadsheet} (updated with new assignment column)

## Output Structure

```
{output_folder}/
├── {homework_pdf} (original, keep as backup)
├── Student Individual Files/
│   ├── {StudentName1}.pdf
│   ├── {StudentName2}.pdf
│   └── ...
└── {completion_spreadsheet} (UPDATED with new assignment column)
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
