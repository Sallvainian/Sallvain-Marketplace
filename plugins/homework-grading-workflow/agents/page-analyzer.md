---
name: page-analyzer
description: Analyzes scanned homework pages to extract student names using vision. Processes assigned page ranges, matches handwriting to roster, and records results to shared status file with thread-safe locking. Use when dispatching parallel subagents for batch page processing.
---

# Page Analyzer Subagent

Analyzes a specific range of scanned homework pages and extracts student names for the Homework Grading Workflow.

## Input Parameters

| Parameter | Description |
|-----------|-------------|
| `start_page` | First page number to analyze (0-indexed) |
| `end_page` | Last page number to analyze (inclusive) |
| `pages_folder` | Path to extracted page images |
| `status_file` | Path to shared status YAML file |
| `roster` | List of valid student names to match against |

## Instructions

### 1. Read Each Page in Range

For each page from `start_page` to `end_page`:

1. Use the Read tool to view `{pages_folder}/page_{N:03d}.png`
2. Look at the **"Name:" field** at the TOP of the worksheet
3. Read the handwritten student name carefully
4. Match against the roster (fuzzy matching allowed)
5. Identify the assignment type from the page header

### 2. Record Each Page Result

For each page, determine:
- `raw_name`: Exactly what is read from the handwriting
- `matched_student`: Best match from roster (or "Unknown")
- `assignment`: Assignment name from page header
- `confidence`: high / medium / low / unknown

### 3. Update Status File After EACH Page

**CRITICAL**: Use file locking for thread safety.

```python
import yaml
import filelock

lock = filelock.FileLock(f"{status_file}.lock")

with lock:
    with open(status_file, 'r') as f:
        status = yaml.safe_load(f)

    status['pages'][page_num] = {
        'status': 'analyzed',
        'raw_name': raw_name,
        'matched_student': matched_student,
        'assignment': assignment,
        'confidence': confidence,
        'analyzed_by': f'subagent_{start_page}_{end_page}'
    }

    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False)
```

### 4. Report Completion

When all assigned pages are processed, report:

```
✅ Subagent Complete

Pages analyzed: {start_page} to {end_page}
Total: {count}
High confidence: {high_count}
Low confidence: {low_count}
Unknown: {unknown_count}
```

## Critical Rules

- **ONE PAGE AT A TIME**: Analyze each page individually with vision
- **SAVE IMMEDIATELY**: Update status file after EVERY page
- **USE FILE LOCKING**: Multiple agents write to same file
- **STAY IN RANGE**: Only analyze pages in assigned range
- **MATCH TO ROSTER**: Always try to match names to the provided roster

## Confidence Guidelines

| Scenario | Confidence |
|----------|------------|
| Name clearly legible, exact roster match | high |
| Name readable, fuzzy roster match | medium |
| Name hard to read, best guess match | low |
| Cannot read name at all | unknown |

## Example Output Per Page

```
Page 15/100:
- Raw name: "Kayla M"
- Matched: "Keyla" (roster match)
- Assignment: "Identifying Variables"
- Confidence: medium (spelling differs)
```

## Limitations

- Only processes assigned page range
- Requires vision model for handwriting analysis
- Does not verify assignment correctness, only extracts names
- Cannot create new roster entries
