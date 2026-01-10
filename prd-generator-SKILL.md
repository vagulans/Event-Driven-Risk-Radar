# PRD Generator Skill

Generate a comprehensive Product Requirements Document from a rough idea or description.

## Purpose

Transform vague project ideas into detailed, actionable PRDs that can be converted to Ralph user stories.

## Output Format

Create a markdown file with this structure:

```markdown
# [Project Name]

## Overview
Brief description of what this project does and why.

## Architecture
High-level system design with components and data flow.

## Module 1: [Name]
**Purpose:** What this module does

**Files:**
- `filename.py` - Description

**Key Classes:**
- `ClassName` - What it does

**Configuration:**
Key settings and their defaults

## Module 2: [Name]
... (repeat for each module)

## Entry Points
How to run the application

## Dependencies
Required packages and versions

## Environment Variables
Configuration via environment
```

## Guidelines

1. **Be Specific**: Include actual file names, class names, function signatures
2. **Be Modular**: Each module should be independently implementable
3. **Be Atomic**: Each section should fit in one context window
4. **Include Code Examples**: Show key interfaces and data structures
5. **Define Dependencies**: List all external packages needed

## Example

User says: "A CLI tool to manage my dotfiles"

Output:

```markdown
# Dotfiles Manager

## Overview
A Python CLI tool for managing dotfiles across machines with support for profiles, templating, and Git sync.

## Module 1: Core (`core/`)
**Purpose:** Core data structures and configuration management

**Files:**
- `config.py` - Configuration loading and validation
- `dotfile.py` - Dotfile representation and operations
- `profile.py` - Profile management

**Key Classes:**
```python
@dataclass
class Dotfile:
    source: Path      # Path in repo
    target: Path      # Path on system (e.g., ~/.bashrc)
    template: bool    # Whether to process as Jinja2
    
class Config:
    def __init__(self, config_path: Path): ...
    def load(self) -> dict: ...
    def validate(self) -> bool: ...
```

## Module 2: CLI (`cli/`)
**Purpose:** Command-line interface using Click

**Files:**
- `main.py` - Entry point and command groups
- `commands/install.py` - Install command
- `commands/sync.py` - Sync command

...
```

## Critical Rules

1. Always include concrete file names and paths
2. Show actual code signatures, not just descriptions
3. Each module must be small enough to implement in ~1 hour
4. Include all configuration options with defaults
5. Specify exact dependency versions where critical
