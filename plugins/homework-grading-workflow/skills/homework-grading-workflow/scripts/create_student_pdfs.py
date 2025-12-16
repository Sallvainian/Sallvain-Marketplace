#!/usr/bin/env python3
"""
Create individual student PDFs from analyzed status file.

Usage: python create_student_pdfs.py <status_file> <source_pdf> <output_folder>

Example: python create_student_pdfs.py ./homework-grading-status.yaml Homework-1.pdf ./output/
"""

import sys
import os

def create_student_pdfs(status_file: str, source_pdf: str, output_folder: str) -> dict:
    """
    Create individual PDF files for each student based on status file.

    Args:
        status_file: Path to homework-grading-status.yaml
        source_pdf: Path to original homework PDF
        output_folder: Directory for output files

    Returns:
        Dict of student -> page count created
    """
    try:
        import fitz  # PyMuPDF
        import yaml
    except ImportError as e:
        print(f"Error: Missing dependency. Run: pip install PyMuPDF pyyaml")
        sys.exit(1)

    # Validate inputs
    if not os.path.exists(status_file):
        print(f"Error: Status file not found: {status_file}")
        sys.exit(1)

    if not os.path.exists(source_pdf):
        print(f"Error: Source PDF not found: {source_pdf}")
        sys.exit(1)

    # Load status
    with open(status_file, 'r') as f:
        status = yaml.safe_load(f)

    # Build student -> pages mapping
    students = {}
    for page_num, page_data in status.get('pages', {}).items():
        student = page_data.get('matched_student', 'Unknown')
        if student == 'Unknown':
            continue

        if student not in students:
            students[student] = []
        students[student].append(int(page_num))

    if not students:
        print("No students found in status file")
        return {}

    # Create output directory
    output_dir = os.path.join(output_folder, 'Student Individual Files')
    os.makedirs(output_dir, exist_ok=True)

    # Open source PDF
    src_pdf = fitz.open(source_pdf)
    results = {}

    for student, pages in students.items():
        if not pages:
            continue

        # Create student PDF
        student_pdf = fitz.open()
        for page_num in sorted(pages):
            if page_num < len(src_pdf):
                student_pdf.insert_pdf(src_pdf, from_page=page_num, to_page=page_num)

        # Save
        output_path = os.path.join(output_dir, f"{student}.pdf")
        student_pdf.save(output_path)
        student_pdf.close()

        results[student] = len(pages)
        print(f"Created: {student}.pdf ({len(pages)} pages)")

    src_pdf.close()
    print(f"\nTotal: {len(results)} student PDFs created")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    status_file = sys.argv[1]
    source_pdf = sys.argv[2]
    output_folder = sys.argv[3]

    create_student_pdfs(status_file, source_pdf, output_folder)
