# Parallel Processing - Subagent Dispatch

## Overview

For large batches (>50 pages), dispatch multiple subagents to process pages simultaneously.

## When to Use Parallel Mode

| Pages | Recommended Mode |
|-------|------------------|
| <50 | Sequential |
| 50-100 | 2 subagents |
| 100-200 | 3-4 subagents |
| >200 | 4 subagents (max) |

## Calculating Subagent Distribution

```python
def calculate_distribution(total_pages, max_subagents=4, pages_per_agent=25):
    num_agents = min(max_subagents, (total_pages + pages_per_agent - 1) // pages_per_agent)
    pages_per = total_pages // num_agents
    remainder = total_pages % num_agents

    ranges = []
    start = 0
    for i in range(num_agents):
        extra = 1 if i < remainder else 0
        end = start + pages_per + extra - 1
        ranges.append((start, end))
        start = end + 1

    return ranges

# Example: 150 pages
# ranges = [(0, 37), (38, 75), (76, 112), (113, 149)]
```

## Dispatch Protocol

**CRITICAL**: Dispatch ALL subagents in a SINGLE message for true parallel execution.

### Subagent Prompt Template

```
Process pages {start_page} to {end_page} for homework grading.

Context:
- Pages folder: {pages_folder}
- Status file: {status_file}
- Roster: {roster_list}

For each page {start_page} to {end_page}:
1. Read page image with vision: {pages_folder}/page_{N:03d}.png
2. Focus on "Name:" field at TOP of worksheet
3. Read handwritten name exactly as written
4. Match to roster (fuzzy matching allowed)
5. Determine confidence: high/medium/low/unknown
6. Identify assignment from page header
7. Update status file with thread-safe locking

After EACH page, update status file:
- Use filelock for thread safety
- Save page_num, raw_name, matched_student, assignment, confidence

Report completion:
✅ Subagent Complete
Pages: {start_page} to {end_page}
Total: {count}
High confidence: {N}
Low confidence: {M}
Unknown: {X}
```

### Using Task Tool

```python
# Dispatch in SINGLE message with multiple Task calls
for start, end in ranges:
    # Task tool call with subagent prompt
    pass
```

## Subagent Status File Updates

Each subagent updates the shared status file with locking:

```python
import yaml
import filelock

def subagent_update(status_file, page_num, page_data):
    lock = filelock.FileLock(f"{status_file}.lock")

    with lock:
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)

        status['pages'][page_num] = page_data

        with open(status_file, 'w') as f:
            yaml.dump(status, f, default_flow_style=False)
```

## Validation After Subagents Complete

After all subagents report completion:

```python
def validate_subagent_results(status_file, total_pages):
    with open(status_file, 'r') as f:
        status = yaml.safe_load(f)

    issues = []

    # Check all pages processed
    for i in range(total_pages):
        if i not in status['pages']:
            issues.append(f"Missing page {i}")

    # Check for anomalies
    student_counts = {}
    for page_data in status['pages'].values():
        student = page_data.get('matched_student', 'Unknown')
        student_counts[student] = student_counts.get(student, 0) + 1

    # Flag if one student has >50% of pages
    for student, count in student_counts.items():
        if count > total_pages * 0.5:
            issues.append(f"Anomaly: {student} has {count}/{total_pages} pages")

    # Check unknown rate
    unknown_count = student_counts.get('Unknown', 0)
    if unknown_count > total_pages * 0.2:
        issues.append(f"High unknown rate: {unknown_count}/{total_pages} pages")

    return issues
```

## Error Recovery

If a subagent fails mid-processing:
1. Check status file for last successful page
2. Identify gap in processed pages
3. Re-dispatch subagent for missing range only
