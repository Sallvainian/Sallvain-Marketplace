#!/usr/bin/env python3
"""
Status tracking for homework grading workflow.

This module provides utilities for:
1. Creating the tracking file (homework-grading-status.yaml)
2. Safely updating progress during page analysis
3. Session resume support (Claude has 99-image limit per session)

Usage as module:
    from update_status import create_tracking_file, update_page, load_tracking_file
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

MAX_IMAGES_PER_SESSION = 99


def create_tracking_file(
    homework_pdf: str,
    roster_file: str,
    period: str,
    output_folder: str,
    completion_spreadsheet: str,
    total_pages: int
) -> Tuple[Dict, str]:
    """
    Create tracking file BEFORE any page analysis.

    This must be called FIRST, before extracting PNGs or reading pages.
    The tracking file enables crash recovery and session resume.

    Args:
        homework_pdf: Path to the homework PDF
        roster_file: Path to roster spreadsheet
        period: Class period (e.g., "Period 4")
        output_folder: Directory for output files
        completion_spreadsheet: Path to completion tracker spreadsheet
        total_pages: Total number of pages in PDF

    Returns:
        Tuple of (status dict, status file path)
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("Required: pip install pyyaml")

    status = {
        'generated': datetime.now().isoformat(),
        'homework_pdf': homework_pdf,
        'roster_file': roster_file,
        'period': period,
        'output_folder': output_folder,
        'completion_spreadsheet': completion_spreadsheet,
        'workflow_status': 'init',
        'total_pages': total_pages,
        'last_analyzed_page': -1,
        'pages_remaining': total_pages,
        'pages': {},
        'students': {},
        'uncertain_pages': [],
        'assignments_found': []
    }

    os.makedirs(output_folder, exist_ok=True)
    status_file = os.path.join(output_folder, 'homework-grading-status.yaml')

    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False, sort_keys=False)

    return status, status_file


def load_tracking_file(output_folder: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Load existing tracking file for resume.

    Args:
        output_folder: Directory containing tracking file

    Returns:
        Tuple of (status dict or None, status file path or None)
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("Required: pip install pyyaml")

    status_file = os.path.join(output_folder, 'homework-grading-status.yaml')

    if not os.path.exists(status_file):
        return None, None

    with open(status_file, 'r') as f:
        status = yaml.safe_load(f)

    return status, status_file


def get_resume_info(status: Dict) -> Tuple[Optional[int], int]:
    """
    Get resume information from tracking file.

    Args:
        status: Status dictionary

    Returns:
        Tuple of (next_page to analyze, pages_remaining)
        Returns (None, 0) if all pages are done
    """
    last_page = status.get('last_analyzed_page', -1)
    total_pages = status['total_pages']

    if last_page >= total_pages - 1:
        return None, 0

    next_page = last_page + 1
    pages_remaining = total_pages - next_page

    return next_page, pages_remaining


def save_status(status: Dict, status_file: str) -> None:
    """
    Save status to file.

    Args:
        status: Status dictionary
        status_file: Path to status file
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("Required: pip install pyyaml")

    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False, sort_keys=False)


def update_page(status: Dict, status_file: str, page_num: int, page_data: Dict[str, Any]) -> None:
    """
    Update tracking file after analyzing a page.

    CRITICAL: Call this after EVERY page for crash recovery.

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
    status['pages_remaining'] = status['total_pages'] - page_num - 1

    # Update workflow status if needed
    if status['workflow_status'] == 'init':
        status['workflow_status'] = 'analyzing'

    # Track uncertain pages
    if page_data.get('confidence') in ['low', 'unknown']:
        if page_num not in status.get('uncertain_pages', []):
            status.setdefault('uncertain_pages', []).append(page_num)

    # Track assignments
    assignment = page_data.get('assignment')
    if assignment and assignment not in status.get('assignments_found', []):
        status.setdefault('assignments_found', []).append(assignment)

    save_status(status, status_file)


def update_page_threadsafe(status_file: str, page_num: int, page_data: Dict[str, Any]) -> None:
    """
    Thread-safe page update for parallel processing.

    Uses file locking to prevent race conditions.

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
        with open(status_file, 'r') as f:
            status = yaml.safe_load(f)

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
            status['pages_remaining'] = status['total_pages'] - page_num - 1

        with open(status_file, 'w') as f:
            yaml.dump(status, f, default_flow_style=False, sort_keys=False)


def check_session_limit(images_read_this_session: int, status: Dict) -> Tuple[bool, str]:
    """
    Check if session limit reached.

    Claude can only read 99 images per session.

    Args:
        images_read_this_session: Number of images read in current session
        status: Status dictionary

    Returns:
        Tuple of (limit_reached: bool, message: str)
    """
    if images_read_this_session >= MAX_IMAGES_PER_SESSION:
        last_page = status.get('last_analyzed_page', -1)
        next_page = last_page + 1
        pages_remaining = status['total_pages'] - next_page

        message = f"""
⚠️ SESSION LIMIT REACHED ({MAX_IMAGES_PER_SESSION} images)

Progress saved to tracking file.
Analyzed pages 0-{last_page}
Pages remaining: {pages_remaining}

To continue:
1. Start a new Claude session
2. Run homework grading workflow again
3. Will resume from page {next_page}
"""
        return True, message

    return False, ""


def display_batch_plan(total_pages: int) -> str:
    """
    Display batch plan for user confirmation.

    Shows how many sessions will be needed based on 99-image limit.

    Args:
        total_pages: Total number of pages in PDF

    Returns:
        Formatted string to display to user
    """
    import math
    sessions_needed = math.ceil(total_pages / MAX_IMAGES_PER_SESSION)

    lines = [
        "",
        "📋 BATCH PLAN",
        f"Total pages: {total_pages}",
        f"Max per session: {MAX_IMAGES_PER_SESSION}",
        f"Sessions needed: {sessions_needed}",
        ""
    ]

    for session_num in range(1, sessions_needed + 1):
        start_page = (session_num - 1) * MAX_IMAGES_PER_SESSION
        end_page = min(session_num * MAX_IMAGES_PER_SESSION - 1, total_pages - 1)
        page_count = end_page - start_page + 1

        lines.append(
            f"  Session {session_num}: pages {start_page}-{end_page} "
            f"({page_count} pages)"
        )

    lines.extend([
        "",
        f"⚠️ This will require {sessions_needed} Claude session(s) to complete.",
        "Continue? (User must confirm)"
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(__doc__)
