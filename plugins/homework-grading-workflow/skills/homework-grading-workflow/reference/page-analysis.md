# Page Analysis - Detailed Instructions

## Overview

Page analysis extracts student names from scanned homework pages using Claude's vision capabilities. This is the **most critical phase** for accuracy.

## The Three Accuracy Rules

1. **One page at a time** - Never batch pages. Analyze each individually.
2. **Focus on Name field** - Look at TOP of worksheet, ignore other text.
3. **Save immediately** - Write to status file after EACH page.

## Step-by-Step Process

### 1. Extract Pages First

Run the extraction script before analysis:

```bash
python scripts/extract_pages.py <homework.pdf> ./pages/
```

This creates `pages/page_000.png`, `pages/page_001.png`, etc.

### 2. Initialize Status Tracking

```python
from scripts.update_status import init_status

status, status_file = init_status(output_folder, total_pages)
start_page = status['last_analyzed_page'] + 1
```

### 3. Analyze Each Page

For EACH page starting from `start_page`:

```python
# Use Read tool to view page
page_path = f"pages/page_{page_num:03d}.png"
# Read tool displays image for vision analysis
```

When viewing the page:

1. **Look at the TOP** - Find "Name:", "Student:", or blank line with handwriting
2. **Read letter by letter** for messy handwriting
3. **Note exactly what you see** - This becomes `raw_name`

### 4. Match to Roster

```python
from difflib import get_close_matches

def match_to_roster(raw_name, roster):
    """Match handwritten name to roster."""
    # Exact match first
    if raw_name in roster:
        return raw_name, 'high'

    # Normalize and try again
    normalized = raw_name.strip().title()
    if normalized in roster:
        return normalized, 'high'

    # Fuzzy match
    matches = get_close_matches(raw_name, roster, n=1, cutoff=0.6)
    if matches:
        return matches[0], 'medium'

    return 'Unknown', 'unknown'
```

### 5. Determine Confidence

| Confidence | Criteria | Action |
|------------|----------|--------|
| high | Name clearly legible, exact roster match | Proceed automatically |
| medium | Name readable, fuzzy match found | Proceed with note |
| low | Name hard to read, best guess | Flag for user review |
| unknown | Cannot read name at all | MUST get user input |

### 6. Identify Assignment Type

Look for assignment identifiers on the page:
- Title/header at top
- "Lesson X" labels
- Worksheet name
- Color indicators (some worksheets are colored)

Common patterns:

| Assignment | Identifier |
|------------|-----------|
| Identifying Variables | "Identifying Variables" header |
| Changes in Kinetic Energy | Blue/colored page |
| Investigation Planning Guide | "Planning Guide" text |
| Force Interaction | "Force Interaction" header |

### 7. Record and Save (CRITICAL)

```python
from scripts.update_status import update_page

page_data = {
    'raw_name': raw_name,
    'matched_student': matched_student,
    'assignment': assignment,
    'confidence': confidence,
    'notes': any_notes
}

update_page(status, status_file, page_num, page_data)
# Status file is saved automatically
```

**SAVE AFTER EVERY PAGE** - This enables crash recovery and session resume.

### 8. Report Template

For each page, report to user:

```
Page {N}/{total}:
- Raw name: "{raw_name}"
- Matched: {matched_student}
- Assignment: {assignment}
- Confidence: {confidence}
```

## Handling Difficult Cases

### Illegible Names

1. Set confidence to `unknown`
2. Set matched_student to `Unknown`
3. Add page to `uncertain_pages`
4. Continue to next page
5. User MUST verify before PDF creation

### Multiple Names (Group Work)

- Use the first/primary name
- Add note: "Group work - using {name} as primary"
- Consider flagging for user review

### Blank Name Field

1. Check if name appears elsewhere on page
2. If truly blank, mark as `Unknown`
3. Flag: "No name field found on page"

### Similar Names on Roster

If roster has James AND Jeremy:
- Read full name carefully
- Check last name if visible
- If still uncertain, set confidence to `low`

## Session Limit Handling

Claude has a 99-image read limit per session.

When approaching limit:

```
Progress saved to status file.
Analyzed pages 0-98.

To continue:
1. Start a new Claude session
2. Run homework grading workflow again
3. It will automatically resume from page 99
```

The status file tracks `last_analyzed_page` for seamless resume.

## Fuzzy Matching Examples

| Raw Name | Roster Match | Confidence | Reason |
|----------|--------------|------------|--------|
| "Keyla M." | Keyla | high | Clear first name match |
| "Eliana L" | Eliomar | low | Different but similar - user verify |
| "J. Smith" | James or Jeremy | low | Ambiguous - user verify |
| "[scribble]" | Unknown | unknown | Cannot read - user MUST verify |
| "Briana" | Briana | high | Exact match |
