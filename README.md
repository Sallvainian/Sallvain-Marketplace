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
- **Session Resume**: Status tracking to continue across sessions

### agent-expert

Expert agent for creating and validating Claude Code agents:

- **Agent Design**: Create agents with proper Markdown + YAML frontmatter structure
- **Validation**: Check against structural requirements (tools, model, description length)
- **Best Practices**: Prompt engineering and domain modeling guidance
- **Templates**: Ready-to-use agent body templates

## Installation

### Option 1: Claude Code Plugin Command (Recommended)

```bash
# Add the marketplace
/plugin marketplace add Sallvainian/Sallvain-Marketplace

# Install a plugin
/plugin install homework-grading-workflow@Sallvain-Marketplace
/plugin install agent-expert@Sallvain-Marketplace
```

### Option 2: Clone and Copy

```bash
# Clone the repository
git clone https://github.com/Sallvainian/Sallvain-Marketplace.git ~/.claude-plugins/Sallvain-Marketplace

# Copy specific plugin to Claude Code
cp -r ~/.claude-plugins/Sallvain-Marketplace/plugins/homework-grading-workflow ~/.claude/plugins/
cp -r ~/.claude-plugins/Sallvain-Marketplace/plugins/agent-expert ~/.claude/plugins/
```

## Usage

### Homework Grading Workflow

Trigger phrases:
- "Process this homework PDF"
- "Organize homework by student"
- "Grade these submissions"
- "Create individual student files from this PDF"

### Agent Expert

Trigger phrases:
- "Create a React performance agent"
- "Design a security audit agent"
- "Validate this agent definition"

## Prerequisites

For the homework grading workflow:

```bash
pip install PyMuPDF pandas openpyxl pyyaml filelock
```

## Repository Structure

```
Sallvain-Marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── plugins/
│   ├── agent-expert/
│   │   ├── plugin.json            # Plugin manifest
│   │   └── agents/
│   │       └── agent-expert.md    # Agent definition
│   └── homework-grading-workflow/
│       ├── plugin.json            # Plugin manifest
│       └── skills/
│           └── homework-grading-workflow/
│               ├── SKILL.md       # Main skill definition
│               ├── reference/     # Reference docs
│               └── scripts/       # Helper scripts
└── README.md
```

## License

Private repository - for personal use only.

## Author

Sallvainian
