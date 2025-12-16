# Clink Integration for Homework Grading

Use PAL MCP's `clink` tool to spawn specialized AI subagents for complex grading scenarios. This provides fresh-context analysis and multi-model validation.

## When to Use Clink

| Scenario | Clink Role | CLI | Purpose |
|----------|------------|-----|---------|
| Illegible names | `default` | gemini | Second opinion on handwritten text |
| Batch planning | `planner` | gemini | Optimize workflow for large PDFs |
| Script issues | `codereviewer` | codex | Debug extraction/creation scripts |
| Status file review | `codereviewer` | claude | Validate tracking file integrity |

## Integration Patterns

### Illegible Name Analysis

When confidence is `unknown` and you can't read a student name, get a second opinion:

```
clink with gemini to analyze this handwritten name on homework page:
- Image path: [page_path]
- Look for name field at TOP of worksheet
- Compare against roster: [student_list]
- Provide best match with confidence level
```

### Batch Planning for Large PDFs

For PDFs with 100+ pages, use planner to optimize session breakdown:

```
clink with gemini planner to optimize homework grading batch plan:
- Total pages: [count]
- Session limit: 99 images
- Students expected: [roster_count]
- Suggest optimal session boundaries to minimize mid-student splits
```

### Script Debugging

When extract_pages.py or create_student_pdfs.py fails:

```
clink with codex codereviewer to debug script failure:
- Script: [script_path]
- Error: [error_message]
- Input files: [paths]
- Identify root cause and suggest fix
```

### Status File Validation

Verify tracking file integrity mid-workflow:

```
clink with claude codereviewer to validate homework-grading-status.yaml:
- Check for gaps in page sequence
- Verify all uncertain_pages are flagged
- Confirm student assignments are consistent
- Identify any data integrity issues
```

### Multi-Model Name Verification

For critical uncertain names, get consensus from multiple models:

```
# Get Gemini's interpretation
clink with gemini to read handwritten name at [path]

# Get Claude's interpretation
clink with claude to read handwritten name at [path]

# Compare results, use consensus or flag for user
```

## Best Practices

1. **Use for uncertain cases only** - Don't spawn clink for every page; reserve for `low`/`unknown` confidence
2. **Pass file paths, not content** - Let the subagent read the image directly
3. **Include roster context** - Always provide the student roster for name matching
4. **Fresh context advantage** - Subagents won't be biased by previous page interpretations
5. **Parallel execution** - Spawn multiple clinks simultaneously for independent page analysis

## Example: Difficult Name Resolution

```
Page 47 analysis:
- Raw name: "[illegible scrawl]"
- Confidence: unknown
- Main context interpretation: "Could be James or Jeremy"

Action: Spawn clink for second opinion

clink with gemini to analyze handwritten name:
  Image: pages/page_047.png
  Name field location: Top of worksheet
  Roster candidates: James Martinez, Jeremy Johnson, Jamie Wilson
  Provide: best match, confidence (high/medium/low), reasoning

Result: "Jeremy Johnson - medium confidence - letter shapes match J-e-r"

Combined assessment: Both interpretations suggest Jeremy
→ Update matched_student to "Jeremy Johnson" with confidence: medium
```

## CLI Selection Guide

| CLI | Strengths for Grading |
|-----|----------------------|
| `gemini` | Large image context, handwriting analysis |
| `claude` | Nuanced reasoning, edge case handling |
| `codex` | Script debugging, code-related issues |
