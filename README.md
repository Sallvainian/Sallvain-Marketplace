# Sallvain-Marketplace

Educational tools for teachers - homework grading, student organization, and classroom management.

## Plugins Available

### homework-grading-workflow

Automate the processing of scanned student homework submissions:

- **PDF Processing**: Extract pages from scanned homework PDFs
- **Student Identification**: Use Claude's vision to read handwritten names
- **Roster Matching**: Match names to your class roster (Excel)
- **Individual Files**: Create separate PDFs per student
- **Completion Tracking**: Generate homework completion checklists

## Installation

### Option 1: Claude Code Plugin Command (Recommended)

```bash
# Add the marketplace
/plugin marketplace add Sallvainian/Sallvain-Marketplace

# Install the plugin
/plugin install homework-grading-workflow@Sallvain-Marketplace
```

### Option 2: Clone and Copy Skills

```bash
# Clone the repository
git clone https://github.com/Sallvainian/Sallvain-Marketplace.git ~/.claude-plugins/Sallvain-Marketplace

# Copy skills to Claude Code skills directory
cp -r ~/.claude-plugins/Sallvain-Marketplace/plugins/homework-grading-workflow/skills/* ~/.claude/skills/
```

## Usage

Once installed, use trigger phrases like:
- "Process this homework PDF"
- "Organize homework by student"
- "Grade these submissions"
- "Create individual student files from this PDF"

## Prerequisites

For the homework grading workflow, you'll need:

```bash
pip install PyMuPDF pandas openpyxl
```

## Repository Structure

```
Sallvain-Marketplace/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace manifest
├── plugins/
│   └── homework-grading-workflow/
│       ├── plugin.json        # Plugin manifest
│       └── skills/
│           └── homework-grading-workflow/
│               └── SKILL.md   # Skill definition
└── README.md
```

## License

Private repository - for personal use only.

## Author

Sallvainian
