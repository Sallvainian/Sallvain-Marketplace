# Troubleshooting Guide

## Common Issues and Solutions

### Unreadable Names

**Symptoms**: Cannot make out handwritten name on page.

**Solutions**:
1. Set confidence to `unknown`
2. Set matched_student to `Unknown`
3. Continue processing other pages
4. Review unknown pages manually before PDF creation

```python
page_data = {
    'status': 'analyzed',
    'raw_name': '[illegible]',
    'matched_student': 'Unknown',
    'confidence': 'unknown',
    'notes': 'Handwriting too messy to read'
}
```

### Session Limit Reached

**Symptoms**: Hit image read limit mid-processing.

**Solutions**:
1. Progress automatically saved to status file
2. Start new session
3. Run workflow again - it will resume from last page

```
Current session: Analyzed pages 0-98
Next session: Will resume from page 99
```

### Missing Students in Output

**Symptoms**: Student on roster but no PDF created.

**Causes**:
- Student didn't submit (correct behavior - no PDF needed)
- Student's pages marked as Unknown
- Name spelling mismatch between page and roster

**Solutions**:
1. Check status file for pages with that student
2. Review uncertain_pages list
3. Manually search page images for the name

### Wrong Pages in Student PDF

**Symptoms**: PDF contains pages from different student.

**Causes**:
- Similar names confused (James vs Jeremy)
- Misread handwriting
- Fuzzy matching too aggressive

**Solutions**:
1. Review page analysis for affected pages
2. Correct matched_student in status file
3. Regenerate PDFs

### Spreadsheet Formula Errors

**Symptoms**: Total column shows errors or wrong values.

**Causes**:
- Column insertion disrupted formula references
- Formula range incorrect

**Solutions**:
1. Check Total formula: should be `=COUNTIF(C{row}:{last_col}{row},"X")`
2. Verify last_col is column before Total
3. Manually fix formula if needed

### Duplicate Student Names

**Symptoms**: Multiple students with same first name.

**Solutions**:
1. Use full names (first + last) for matching
2. Check period number on worksheet
3. Add disambiguation to status file

```python
# Handle duplicates
if raw_name in ['James', 'Jeremy']:
    # Check last name or other identifiers
    full_name = extract_full_name(page_image)
```

### PDF Creation Fails

**Symptoms**: Error when creating student PDFs.

**Causes**:
- Source PDF locked or corrupted
- Invalid page numbers in mapping
- Disk space issues

**Solutions**:
1. Verify source PDF opens correctly
2. Check page numbers are within range
3. Ensure sufficient disk space

```python
# Validate before creating
src = fitz.open(homework_pdf)
max_page = len(src) - 1

for page_num in data['pages']:
    if page_num > max_page:
        print(f"Invalid page {page_num} (max is {max_page})")
```

### Missing Pages in Status File

**Symptoms**: Some pages not recorded in status file.

**Causes**:
- Session interrupted mid-processing
- Page was skipped due to error
- Status file not saved after page analysis

**Solutions**:
1. Check status file for gaps in page numbers
2. Resume workflow to process missing pages
3. Manually add missing pages to status file if needed

```python
# Find missing pages
missing = [i for i in range(total_pages) if i not in status['pages']]
if missing:
    print(f"Re-process pages: {missing}")
```

## Recovery Procedures

### Full Reset

If workflow is in bad state:

```bash
# Remove status file to start fresh
rm homework-grading-status.yaml
rm -rf pages/
rm -rf "Student Individual Files/"

# Re-run workflow from beginning
```

### Partial Recovery

To fix specific pages without full reset:

1. Edit status file directly
2. Correct the affected page entries
3. Run verification phase
4. Regenerate PDFs if needed

### Backup Restoration

If original PDF or spreadsheet corrupted:

1. Restore from backup
2. Clear workflow outputs
3. Re-run workflow

## Prevention Tips

1. **Save frequently** - Status saves after each page
2. **Verify early** - Check first few PDFs before processing all
3. **Keep backups** - Don't modify original files
4. **Review uncertain pages** - Don't skip manual verification
