# Homework Grading Workflow - Decision Flowchart

## Main Workflow Decision Tree

```
START: User provides homework PDF
│
├── PHASE 0: PLANNING (BEFORE ANYTHING ELSE)
│   │
│   ├── Open PDF, count pages
│   │   └── doc = fitz.open(pdf); total = len(doc)
│   │
│   ├── Tracking file exists?
│   │   ├── YES → Resume mode (skip to "Check tracking file")
│   │   └── NO → Create new tracking file
│   │
│   ├── Calculate batch plan
│   │   └── sessions = ceil(total_pages / 99)
│   │
│   ├── Create tracking file (homework-grading-status.yaml) with:
│   │   ├── homework_pdf, roster_file, period, output_folder
│   │   ├── total_pages, last_analyzed_page = -1
│   │   └── pages: {}, uncertain_pages: [], assignments_found: []
│   │
│   ├── Display batch plan to user:
│   │   └── "150 pages = 2 sessions (99 + 51)"
│   │
│   └── User confirms?
│       ├── NO → Stop, user not ready
│       └── YES → Continue to Phase 1
│
├── PHASE 1: SETUP
│   │
│   ├── Have roster spreadsheet?
│   │   ├── NO → Ask user for roster file
│   │   └── YES → Continue
│   │
│   ├── Invoke xlsx skill
│   │   └── Load roster for target period
│   │
│   └── Extract PDF pages to images
│       └── python scripts/extract_pages.py <pdf> <output>
│
├── PHASE 2: PAGE ANALYSIS
│   │
│   ├── Check tracking file for resume info
│   │   └── start_page = last_analyzed_page + 1
│   │
│   └── FOR EACH PAGE (one at a time, max 99 per session):
│       ├── Read page with Read tool
│       ├── Find Name field at TOP
│       ├── Match to roster
│       │   ├── Exact match → confidence: high
│       │   ├── Fuzzy match → confidence: medium
│       │   ├── Uncertain → confidence: low (flag for review)
│       │   └── Unreadable → confidence: unknown (MUST ask user)
│       ├── Save to tracking file IMMEDIATELY after each page
│       └── Hit 99-image limit? → STOP, inform user to resume in new session
│
├── All pages analyzed?
│   ├── NO → Continue analysis or resume in new session
│   └── YES → Continue
│
├── Have uncertain/unknown pages?
│   ├── YES → Show user EACH uncertain page
│   │   └── User confirms/corrects → Update status
│   └── NO → Continue
│
├── Create student PDFs
│   └── python scripts/create_student_pdfs.py <status> <pdf> <output>
│
├── VERIFY each PDF created
│   └── FOR EACH PDF: Open, check all pages belong to that student
│
├── Update completion spreadsheet?
│   ├── NO → Skip to cleanup
│   └── YES → Invoke xlsx skill, add column, mark X, update Total
│
├── Cleanup
│   └── rm -rf pages/
│
└── DONE: Report summary
```

## Decision: Which Confidence Level?

```
Reading a page's Name field:
│
├── Name clearly legible AND exact roster match?
│   └── confidence: high
│
├── Name readable AND fuzzy roster match (similar spelling)?
│   └── confidence: medium
│
├── Name hard to read, making best guess?
│   └── confidence: low (add to uncertain_pages)
│
└── Cannot read name at all?
    └── confidence: unknown (MUST ask user before PDF creation)
```

## Decision: When to Ask User

```
Uncertain page detected:
│
├── confidence == 'low'?
│   └── FLAG for user review after analysis phase
│
├── confidence == 'unknown'?
│   └── MUST get user confirmation before creating PDFs
│
├── Name matches multiple roster entries?
│   └── ASK user to disambiguate
│
└── Page appears blank or has no name field?
    └── ASK user: "Is this a valid submission page?"
```

## Decision: Session Management

```
Starting workflow:
│
├── Tracking file exists in output folder?
│   │
│   ├── YES → Resume mode
│   │   ├── Read homework-grading-status.yaml
│   │   ├── last_analyzed_page < total_pages - 1?
│   │   │   └── RESUME from last_analyzed_page + 1
│   │   └── All pages analyzed?
│   │       └── SKIP to PDF creation phase
│   │
│   └── NO → Phase 0: Create tracking file
│       ├── Count pages in PDF
│       ├── Display batch plan: "150 pages = 2 sessions"
│       ├── Get user confirmation
│       └── Create homework-grading-status.yaml

During analysis:
│
├── Image read count = 99 this session?
│   └── SAVE to tracking file, inform user:
│       "Session limit reached. Analyzed pages 0-98."
│       "Resume workflow in new session to continue from page 99."
```
