# =============================================================================
# AUTO-RALPH BOILERPLATE
# =============================================================================
# Clone this repo, drop in a rough idea or PRD, and let Amp + Ralph build it.
#
# Quick Start:
#   just init                    # First time setup
#   just new "my app idea"       # Generate PRD from idea
#   just convert my-prd.md       # Convert existing PRD to stories
#   just go                      # Run Ralph
#
# Prerequisites: amp CLI, jq, git
# =============================================================================

set dotenv-load

# Default
default:
    @just --list

# --- SETUP -------------------------------------------------------------------

# Initialize everything (run once after cloning)
init: _check-deps _install-skills _init-git
    @echo ""
    @echo "✅ Auto-Ralph ready!"
    @echo ""
    @echo "Next: just new 'describe your project idea'"
    @echo "  Or: just convert YOUR_PRD.md"

_check-deps:
    #!/usr/bin/env bash
    echo "🔍 Checking dependencies..."
    command -v amp >/dev/null || { echo "❌ amp CLI not found"; exit 1; }
    command -v jq >/dev/null || { echo "❌ jq not found (brew install jq)"; exit 1; }
    command -v git >/dev/null || { echo "❌ git not found"; exit 1; }
    echo "✅ Dependencies OK"

_install-skills:
    #!/usr/bin/env bash
    echo "📦 Installing Amp skills..."
    SKILLS_DIR="${HOME}/.config/amp/skills"
    mkdir -p "$SKILLS_DIR"
    cp -r skills/* "$SKILLS_DIR/" 2>/dev/null || true
    echo "✅ Skills installed to $SKILLS_DIR"

_init-git:
    #!/usr/bin/env bash
    if [ ! -d ".git" ]; then
        git init --quiet
        git add -A
        git commit -m "Initial commit" --quiet 2>/dev/null || true
    fi

# --- PROJECT CREATION --------------------------------------------------------

# Generate a PRD from a rough idea (Amp does the thinking)
new idea:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🧠 Generating PRD from idea..."
    echo ""
    
    amp "Load the prd-generator skill. Create a detailed PRD for: {{idea}}. Save to prd.md"
    
    if [ -f "prd.md" ]; then
        echo ""
        echo "✅ PRD created: prd.md"
        echo ""
        echo "Next: Review prd.md, then run 'just convert prd.md'"
    fi

# Convert markdown PRD to Ralph stories (Amp does the thinking)
convert prd_file:
    #!/usr/bin/env bash
    set -euo pipefail
    
    if [ ! -f "{{prd_file}}" ]; then
        echo "❌ File not found: {{prd_file}}"
        exit 1
    fi
    
    mkdir -p scripts/ralph
    
    echo "🔄 Converting PRD to Ralph stories..."
    echo ""
    
    amp "Load the prd-converter skill. Convert {{prd_file}} to scripts/ralph/prd.json. Follow the skill instructions exactly."
    
    if [ -f "scripts/ralph/prd.json" ]; then
        echo ""
        echo "✅ Converted to scripts/ralph/prd.json"
        echo ""
        echo "📊 Stories:"
        jq -r '.userStories[] | "  " + (if .passes then "✅" else "⬜" end) + " [" + .id + "] " + .title' scripts/ralph/prd.json
        echo ""
        echo "Next: just go"
    fi

# --- RALPH EXECUTION ---------------------------------------------------------

# Run Ralph (default 10 iterations)
go iterations="10":
    #!/usr/bin/env bash
    set -euo pipefail
    
    if [ ! -f "scripts/ralph/prd.json" ]; then
        echo "❌ No prd.json found"
        echo "Run: just convert YOUR_PRD.md"
        exit 1
    fi
    
    # Ensure ralph files exist
    just _ensure-ralph-files
    
    echo "🚀 Starting Ralph ({{iterations}} iterations max)"
    echo ""
    
    cd scripts/ralph && ./ralph.sh {{iterations}}

# Single iteration (human-in-the-loop)
step:
    @just go 1

# --- STATUS ------------------------------------------------------------------

# Show current progress
status:
    #!/usr/bin/env bash
    if [ ! -f "scripts/ralph/prd.json" ]; then
        echo "No project loaded. Run 'just new' or 'just convert'"
        exit 0
    fi
    
    echo "📊 Project: $(jq -r '.project' scripts/ralph/prd.json)"
    echo "🌿 Branch: $(jq -r '.branchName' scripts/ralph/prd.json)"
    echo ""
    
    TOTAL=$(jq '.userStories | length' scripts/ralph/prd.json)
    DONE=$(jq '[.userStories[] | select(.passes == true)] | length' scripts/ralph/prd.json)
    echo "Progress: $DONE / $TOTAL"
    echo ""
    
    jq -r '.userStories[] | "  " + (if .passes then "✅" else "⬜" end) + " [" + .id + "] " + .title' scripts/ralph/prd.json

# Show recent progress log
log:
    @tail -50 scripts/ralph/progress.txt 2>/dev/null || echo "No progress yet"

# Watch progress in real-time
watch:
    @tail -f scripts/ralph/progress.txt

# --- MAINTENANCE -------------------------------------------------------------

# Archive current project and reset
reset:
    #!/usr/bin/env bash
    if [ -f "scripts/ralph/prd.json" ]; then
        BRANCH=$(jq -r '.branchName // "unknown"' scripts/ralph/prd.json | sed 's|^ralph/||')
        ARCHIVE="archive/$(date +%Y-%m-%d)-${BRANCH}"
        mkdir -p "$ARCHIVE"
        mv scripts/ralph/prd.json "$ARCHIVE/" 2>/dev/null || true
        mv scripts/ralph/progress.txt "$ARCHIVE/" 2>/dev/null || true
        rm -f scripts/ralph/.last-branch
        echo "📦 Archived to $ARCHIVE"
    fi
    just _init-progress
    echo "✅ Reset complete"

# Edit files
edit-prd:
    @${EDITOR:-vim} scripts/ralph/prd.json

edit-prompt:
    @${EDITOR:-vim} scripts/ralph/prompt.md

# --- INTERNAL ----------------------------------------------------------------

_ensure-ralph-files:
    #!/usr/bin/env bash
    mkdir -p scripts/ralph
    
    # Create ralph.sh if missing
    if [ ! -f "scripts/ralph/ralph.sh" ]; then
        cat > scripts/ralph/ralph.sh << 'RALPH_SH'
#!/bin/bash
set -e

MAX_ITERATIONS=${1:-10}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd.json"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
PROMPT_FILE="$SCRIPT_DIR/prompt.md"

if [ ! -f "$PRD_FILE" ]; then
    echo "Error: prd.json not found"
    exit 1
fi

# Check if all stories are done
all_done() {
    local remaining=$(jq '[.userStories[] | select(.passes == false)] | length' "$PRD_FILE")
    [ "$remaining" -eq 0 ]
}

echo "🚀 Ralph starting (max $MAX_ITERATIONS iterations)"
echo ""

for i in $(seq 1 $MAX_ITERATIONS); do
    if all_done; then
        echo ""
        echo "✅ All stories complete!"
        echo "<promise>COMPLETE</promise>"
        exit 0
    fi
    
    NEXT_STORY=$(jq -r '[.userStories[] | select(.passes == false)] | sort_by(.priority) | .[0].title' "$PRD_FILE")
    echo "[$i/$MAX_ITERATIONS] Working on: $NEXT_STORY"
    
    # Run amp with the prompt
    cat "$PROMPT_FILE" | amp --print
    
    echo ""
done

echo "⚠️  Max iterations reached. Run 'just go' to continue."
RALPH_SH
        chmod +x scripts/ralph/ralph.sh
    fi
    
    # Create prompt.md if missing
    if [ ! -f "scripts/ralph/prompt.md" ]; then
        cat > scripts/ralph/prompt.md << 'PROMPT_MD'
# Ralph Iteration

You are in a Ralph loop. Each iteration you:
1. Read prd.json and progress.txt
2. Pick the highest priority story where passes: false
3. Implement ONLY that story
4. Run tests/checks
5. If passing, commit and mark story as passes: true
6. Update progress.txt with learnings

## Instructions

1. Read `scripts/ralph/prd.json` for the task list
2. Read `scripts/ralph/progress.txt` for context from previous iterations
3. Read `AGENTS.md` for project conventions

4. Find the highest priority incomplete story (passes: false)

5. Implement ONLY that one story:
   - Create/modify files as needed
   - Follow acceptance criteria exactly
   - Keep changes minimal and focused

6. Verify your work:
   - Run any relevant tests
   - Check types if applicable
   - Ensure imports work

7. If verification passes:
   - Commit with message: "[Ralph] {story.id}: {story.title}"
   - Update prd.json: set that story's passes to true
   - Append to progress.txt what you learned

8. If ALL stories are complete, output: <promise>COMPLETE</promise>

## Critical Rules
- ONE story per iteration
- COMMIT after each successful story
- UPDATE prd.json passes field
- APPEND learnings to progress.txt
PROMPT_MD
    fi
    
    just _init-progress

_init-progress:
    #!/usr/bin/env bash
    if [ ! -f "scripts/ralph/progress.txt" ]; then
        mkdir -p scripts/ralph
        cat > scripts/ralph/progress.txt << 'PROGRESS'
# Progress Log

## Patterns Discovered
<!-- Ralph adds codebase patterns here -->

## Session Log
<!-- Ralph appends learnings here -->
PROGRESS
    fi

# Create AGENTS.md if missing
_init-agents:
    #!/usr/bin/env bash
    if [ ! -f "AGENTS.md" ]; then
        cat > AGENTS.md << 'AGENTS'
# Project Conventions

## Structure
<!-- Project structure notes -->

## Patterns
<!-- Code patterns to follow -->

## Gotchas
<!-- Things to watch out for -->
AGENTS
    fi
