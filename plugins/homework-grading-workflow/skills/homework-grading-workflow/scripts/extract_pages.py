#!/usr/bin/env python3
"""
Extract PDF pages as images for vision analysis.

Usage: python extract_pages.py <input_pdf> <output_folder>

Example: python extract_pages.py Homework-1.pdf ./pages/
"""

import sys
import os

def extract_pages(input_pdf: str, output_folder: str, dpi: int = 150) -> int:
    """
    Extract all pages from PDF as PNG images.

    Args:
        input_pdf: Path to source PDF
        output_folder: Directory for output images
        dpi: Resolution for image extraction (default 150)

    Returns:
        Total number of pages extracted
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Error: PyMuPDF not installed. Run: pip install PyMuPDF")
        sys.exit(1)

    # Validate input
    if not os.path.exists(input_pdf):
        print(f"Error: PDF not found: {input_pdf}")
        sys.exit(1)

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Open PDF
    doc = fitz.open(input_pdf)
    total_pages = len(doc)
    print(f"Extracting {total_pages} pages from {input_pdf}")

    # Extract each page
    for i in range(total_pages):
        page_path = os.path.join(output_folder, f"page_{i:03d}.png")

        # Skip if already extracted
        if os.path.exists(page_path):
            print(f"  Skipping page {i} (already exists)")
            continue

        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        pix.save(page_path)
        print(f"  Extracted page {i}/{total_pages - 1}")

    doc.close()
    print(f"Done: {total_pages} pages in {output_folder}")
    return total_pages


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_folder = sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150

    extract_pages(input_pdf, output_folder, dpi)
