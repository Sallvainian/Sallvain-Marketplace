# Status Tracking - Schema and Usage

## Overview

The status file (`homework-grading-status.yaml`) tracks workflow progress for crash recovery and session resumption.

## Status File Schema

```yaml
# Metadata
generated: "2024-01-15T10:30:00"
workflow_status: analyzing  # analyzing | creating_pdfs | updating_spreadsheet | verifying | complete

# Progress tracking
total_pages: 150
last_analyzed_page: 75  # Resume from here

# Page data
pages:
  0:
    status: analyzed
    raw_name: "Keyla Martinez"
    matched_student: "Keyla"
    assignment: "Identifying Variables"
    confidence: high
  1:
    status: analyzed
    raw_name: "Keyla M"
    matched_student: "Keyla"
    assignment: "Identifying Variables"
    confidence: high
  # ... more pages

# Aggregated data
students:
  Keyla:
    pages: [0, 1]
    assignments: ["Identifying Variables"]
  Briana:
    pages: [2]
    assignments: ["Identifying Variables"]

# Review lists
uncertain_pages: [45, 67, 89]
assignments_found: ["Identifying Variables", "Force Interaction"]
```

## Initialization

```python
import yaml
import os
from datetime import datetime

def init_status(output_folder, total_pages):
    status_file = os.path.join(output_folder, 'homework-grading-status.yaml')

    if os.path.exists(status_file):
        # Resume mode
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)
        print(f"Resuming from page {status.get('last_analyzed_page', -1) + 1}")
        return status, status_file

    # New status
    status = {
        'generated': datetime.now().isoformat(),
        'workflow_status': 'analyzing',
        'total_pages': total_pages,
        'last_analyzed_page': -1,
        'pages': {},
        'students': {},
        'uncertain_pages': [],
        'assignments_found': []
    }

    save_status(status, status_file)
    return status, status_file
```

## Saving Status

```python
def save_status(status, status_file):
    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False, sort_keys=False)
```

## Updating After Each Page

```python
def update_page(status, status_file, page_num, page_data):
    status['pages'][page_num] = page_data
    status['last_analyzed_page'] = page_num

    # Track uncertain pages
    if page_data.get('confidence') in ['low', 'unknown']:
        if page_num not in status['uncertain_pages']:
            status['uncertain_pages'].append(page_num)

    # Track assignments
    assignment = page_data.get('assignment')
    if assignment and assignment not in status['assignments_found']:
        status['assignments_found'].append(assignment)

    save_status(status, status_file)
```

## Thread-Safe Updates (Parallel Mode)

For parallel subagent processing, use file locking:

```python
import filelock

def update_page_threadsafe(status_file, page_num, page_data):
    lock = filelock.FileLock(f"{status_file}.lock")

    with lock:
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)

        status['pages'][page_num] = page_data

        # Update last_analyzed_page only if all prior pages done
        if all(i in status['pages'] for i in range(page_num)):
            status['last_analyzed_page'] = page_num

        with open(status_file, 'w') as f:
            yaml.dump(status, f, default_flow_style=False)
```

## Workflow Status Transitions

```
analyzing → creating_pdfs → updating_spreadsheet → verifying → complete
```

Update status as workflow progresses:

```python
status['workflow_status'] = 'creating_pdfs'
save_status(status, status_file)
```
