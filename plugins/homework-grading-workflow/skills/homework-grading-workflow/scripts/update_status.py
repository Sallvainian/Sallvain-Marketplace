#!/usr/bin/env python3
"""
Thread-safe status file operations for homework grading workflow.

This module provides utilities for safely updating the shared status file
when multiple subagents are processing pages in parallel.

Usage as module:
    from update_status import init_status, update_page, save_status
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

def init_status(output_folder: str, total_pages: int) -> Tuple[Dict, str]:
    """
    Initialize or resume status tracking.

    Args:
        output_folder: Directory containing status file
        total_pages: Total number of pages to process

    Returns:
        Tuple of (status dict, status file path)
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required. Run: pip install pyyaml")

    status_file = os.path.join(output_folder, 'homework-grading-status.yaml')

    if os.path.exists(status_file):
        # Resume mode
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)
        last_page = status.get('last_analyzed_page', -1)
        print(f"Resuming from page {last_page + 1}")
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
    print(f"Created new status file: {status_file}")
    return status, status_file


def save_status(status: Dict, status_file: str) -> None:
    """
    Save status to file (non-locking version for sequential processing).

    Args:
        status: Status dictionary
        status_file: Path to status file
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("pyyaml required. Run: pip install pyyaml")

    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False, sort_keys=False)


def update_page_threadsafe(status_file: str, page_num: int, page_data: Dict[str, Any]) -> None:
    """
    Thread-safe page update for parallel subagent processing.

    Uses file locking to prevent race conditions when multiple subagents
    update the same status file.

    Args:
        status_file: Path to status file
        page_num: Page number being updated
        page_data: Dict with raw_name, matched_student, assignment, confidence
    """
    try:
        import yaml
        import filelock
    except ImportError as e:
        raise ImportError("Required: pip install pyyaml filelock")

    lock = filelock.FileLock(f"{status_file}.lock", timeout=30)

    with lock:
        # Read current state
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)

        # Update page entry
        status['pages'][page_num] = {
            'status': 'analyzed',
            **page_data
        }

        # Track uncertain pages
        if page_data.get('confidence') in ['low', 'unknown']:
            if page_num not in status.get('uncertain_pages', []):
                status.setdefault('uncertain_pages', []).append(page_num)

        # Track assignments
        assignment = page_data.get('assignment')
        if assignment and assignment not in status.get('assignments_found', []):
            status.setdefault('assignments_found', []).append(assignment)

        # Update last_analyzed_page only if all prior pages done
        all_prior_done = all(i in status['pages'] for i in range(page_num))
        if all_prior_done:
            status['last_analyzed_page'] = page_num

        # Write back
        with open(status_file, 'w') as f:
            yaml.dump(status, f, default_flow_style=False, sort_keys=False)


def update_page(status: Dict, status_file: str, page_num: int, page_data: Dict[str, Any]) -> None:
    """
    Update page in status dict and save (sequential processing version).

    Args:
        status: Status dictionary to update
        status_file: Path to status file
        page_num: Page number being updated
        page_data: Dict with raw_name, matched_student, assignment, confidence
    """
    status['pages'][page_num] = {
        'status': 'analyzed',
        **page_data
    }
    status['last_analyzed_page'] = page_num

    # Track uncertain pages
    if page_data.get('confidence') in ['low', 'unknown']:
        if page_num not in status.get('uncertain_pages', []):
            status.setdefault('uncertain_pages', []).append(page_num)

    # Track assignments
    assignment = page_data.get('assignment')
    if assignment and assignment not in status.get('assignments_found', []):
        status.setdefault('assignments_found', []).append(assignment)

    save_status(status, status_file)


if __name__ == "__main__":
    print(__doc__)
