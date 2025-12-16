# Page Analysis - Detailed Instructions

## Overview

Page analysis extracts student names from scanned homework pages using vision capabilities.

## Step-by-Step Process

### 1. Load Page Image

```python
# Use Read tool to view each page
page_path = f"{pages_folder}/page_{page_num:03d}.png"
# Read tool displays image for vision analysis
```

### 2. Locate the Name Field

Look at the **TOP** of the worksheet for:
- "Name:" label
- "Student:" label
- Blank line with handwriting near top

### 3. Read the Handwritten Name

1. Identify each letter carefully
2. For messy handwriting, read letter-by-letter
3. Note exactly what is written (raw_name)

### 4. Match to Roster

```python
# Fuzzy matching logic
def match_to_roster(raw_name, roster):
    # Exact match first
    if raw_name in roster:
        return raw_name, 'high'

    # Fuzzy match
    from difflib import get_close_matches
    matches = get_close_matches(raw_name, roster, n=1, cutoff=0.6)
    if matches:
        return matches[0], 'medium'

    return 'Unknown', 'unknown'
```

### 5. Determine Confidence Level

| Confidence | Criteria |
|------------|----------|
| high | Name clearly legible, exact roster match |
| medium | Name readable, fuzzy roster match |
| low | Name hard to read, best guess match |
| unknown | Cannot read name at all |

### 6. Identify Assignment Type

Look for assignment identifiers:
- Page title/header
- Worksheet name
- Lesson number

### 7. Record Page Data

```python
page_data = {
    'status': 'analyzed',
    'raw_name': raw_name,        # Exactly what was read
    'matched_student': student,   # Roster match
    'assignment': assignment,     # Assignment name
    'confidence': confidence      # high/medium/low/unknown
}
```

### 8. Save After EACH Page

**CRITICAL**: Save status file after every page for crash recovery.

```python
status['pages'][page_num] = page_data
status['last_analyzed_page'] = page_num

with open(status_file, 'w') as f:
    yaml.dump(status, f, default_flow_style=False)
```

## Page Analysis Template

For each page, report:

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
3. Add to uncertain_pages list
4. Continue to next page

### Multiple Names

If page has multiple names (group work):
- Use the first/primary name
- Note in status that page has multiple names

### Blank Name Field

1. Check if name appears elsewhere on page
2. If truly blank, mark as `Unknown`
3. Flag for manual review
