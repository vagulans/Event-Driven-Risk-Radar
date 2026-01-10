# Auto-Ralph Boilerplate

Clone → Drop PRD → Let Amp + Ralph build it.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOU/auto-ralph-boilerplate my-project
cd my-project

# 2. Initialize (installs Amp skills)
just init

# 3. Option A: Generate PRD from idea
just new "a Python CLI for managing AWS Lambda functions"

# 3. Option B: Drop existing PRD
cp ~/my-prd.md ./prd.md

# 4. Convert PRD to Ralph stories
just convert prd.md

# 5. Let Ralph build it
just go 20
```

## Commands

| Command | Description |
|---------|-------------|
| `just init` | First-time setup (install skills, init git) |
| `just new "idea"` | Generate PRD from rough idea |
| `just convert FILE.md` | Convert markdown PRD to stories |
| `just go [N]` | Run Ralph loop (default 10 iterations) |
| `just step` | Single iteration (human-in-the-loop) |
| `just status` | Show progress |
| `just log` | Show recent progress log |
| `just watch` | Watch progress in real-time |
| `just reset` | Archive current project and start fresh |

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Your Idea  │ ──▶ │     PRD     │ ──▶ │   Stories   │ ──▶ │    Code     │
│             │     │   (prd.md)  │     │ (prd.json)  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                         │                    │                    │
                    prd-generator        prd-converter          ralph
                       skill                skill               loop
```

1. **PRD Generator Skill**: Transforms vague ideas into detailed PRDs with file names, classes, and code signatures
2. **PRD Converter Skill**: Breaks PRD into atomic stories (one context window each)
3. **Ralph Loop**: Iteratively implements each story, commits, and moves to next

## Prerequisites

- [amp CLI](https://ampcode.com) installed and authenticated
- [just](https://github.com/casey/just) command runner
- `jq` for JSON processing
- `git`

```bash
# macOS
brew install just jq

# Check amp
amp --version
```

## File Structure

```
auto-ralph-boilerplate/
├── justfile              # All commands
├── skills/
│   ├── prd-generator/    # Idea → PRD skill
│   │   └── SKILL.md
│   └── prd-converter/    # PRD → Stories skill
│       └── SKILL.md
├── scripts/ralph/        # Created on first run
│   ├── ralph.sh          # The loop script
│   ├── prompt.md         # Per-iteration prompt
│   ├── prd.json          # Your stories
│   └── progress.txt      # Learning log
└── AGENTS.md             # Project conventions (Ralph updates this)
```

## Tips

### Write Better PRDs

The more specific your PRD, the better Ralph performs:

```markdown
# Good PRD
## Module: Auth (`auth/`)
**Files:**
- `models.py` - User and Session dataclasses
- `jwt.py` - Token generation/validation

**Key Classes:**
```python
@dataclass
class User:
    id: str
    email: str
    hashed_password: str
```

# Vague PRD (Ralph will struggle)
## Authentication
Handle user login and sessions
```

### Human-in-the-Loop

For complex projects, use `just step` to run one iteration at a time:

```bash
just step          # Run one iteration
just status        # Check what happened
just edit-prd      # Adjust stories if needed
just step          # Next iteration
```

### Recovering from Stuck States

If Ralph gets stuck:

```bash
just status        # See where it's stuck
just edit-prd      # Simplify the stuck story's criteria
just step          # Try again
```

## Customization

### Custom Prompt

Edit `scripts/ralph/prompt.md` to add project-specific instructions:

```markdown
## Project-Specific Rules
- Always use async/await for I/O
- Follow Google Python style guide
- Use pytest for all tests
```

### Amp Settings

For large stories, enable auto-handoff in `~/.config/amp/settings.json`:

```json
{
  "amp.experimental.autoHandoff": { "context": 90 }
}
```

## License

MIT
