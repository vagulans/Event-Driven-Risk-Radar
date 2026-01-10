# =============================================================================
# AUTO-RALPH BOILERPLATE
# =============================================================================
# just init                    # First time setup
# just new "my app idea"       # Generate PRD from idea
# just convert my-prd.md       # Convert existing PRD to stories  
# just go                      # Run Ralph
# =============================================================================

set dotenv-load

default:
    @just --list

# --- SETUP -------------------------------------------------------------------

# Initialize everything (run once after cloning)
init: _check-deps _install-skills _init-git _init-agents
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

_init-agents:
    #!/usr/bin/env bash
    if [ ! -f "AGENTS.md" ]; then
        echo "# Project Conventions" > AGENTS.md
    fi

# --- PROJECT CREATION --------------------------------------------------------

# Generate a PRD from a rough idea
new idea:
    #!/usr/bin/env bash
    echo "🧠 Generating PRD from idea..."
    echo "Load the prd-generator skill. Create a detailed PRD for: {{idea}}. Save to prd.md" | amp -x --dangerously-allow-all
    if [ -f "prd.md" ]; then
        echo "✅ PRD created: prd.md"
        echo "Next: just convert prd.md"
    fi

# Convert markdown PRD to Ralph stories
convert prd_file:
    #!/usr/bin/env bash
    if [ ! -f "{{prd_file}}" ]; then
        echo "❌ File not found: {{prd_file}}"
        exit 1
    fi
    mkdir -p scripts/ralph
    echo "🔄 Converting PRD to Ralph stories..."
    echo "Load the prd-converter skill. Convert {{prd_file}} to scripts/ralph/prd.json" | amp -x --dangerously-allow-all
    if [ -f "scripts/ralph/prd.json" ]; then
        echo "✅ Converted!"
        jq -r '.userStories[] | "  ⬜ [" + .id + "] " + .title' scripts/ralph/prd.json
        echo ""
        echo "Next: just go"
    fi

# --- RALPH EXECUTION ---------------------------------------------------------

# Run Ralph loop
go iterations="10":
    #!/usr/bin/env bash
    if [ ! -f "scripts/ralph/prd.json" ]; then
        echo "❌ No prd.json. Run: just convert YOUR_PRD.md"
        exit 1
    fi
    just _setup-ralph
    echo "🚀 Starting Ralph ({{iterations}} iterations)"
    bash scripts/ralph/ralph.sh {{iterations}}

# Single iteration
step:
    @just go 1

# --- STATUS ------------------------------------------------------------------

# Show progress
status:
    #!/usr/bin/env bash
    if [ ! -f "scripts/ralph/prd.json" ]; then
        echo "No project. Run 'just new' or 'just convert'"
        exit 0
    fi
    echo "📊 $(jq -r '.project' scripts/ralph/prd.json)"
    TOTAL=$(jq '.userStories | length' scripts/ralph/prd.json)
    DONE=$(jq '[.userStories[] | select(.passes == true)] | length' scripts/ralph/prd.json)
    echo "Progress: $DONE / $TOTAL"
    echo ""
    jq -r '.userStories[] | (if .passes then "  ✅" else "  ⬜" end) + " [" + .id + "] " + .title' scripts/ralph/prd.json

log:
    @tail -50 scripts/ralph/progress.txt 2>/dev/null || echo "No progress yet"

watch:
    @tail -f scripts/ralph/progress.txt

# --- MAINTENANCE -------------------------------------------------------------

reset:
    #!/usr/bin/env bash
    if [ -f "scripts/ralph/prd.json" ]; then
        NAME=$(jq -r '.branchName // "backup"' scripts/ralph/prd.json | sed 's|ralph/||')
        mkdir -p "archive/$(date +%Y-%m-%d)-$NAME"
        mv scripts/ralph/prd.json "archive/$(date +%Y-%m-%d)-$NAME/" 2>/dev/null || true
        mv scripts/ralph/progress.txt "archive/$(date +%Y-%m-%d)-$NAME/" 2>/dev/null || true
        echo "📦 Archived"
    fi
    rm -f scripts/ralph/.last-branch
    echo "✅ Reset"

edit-prd:
    @${EDITOR:-vim} scripts/ralph/prd.json

edit-prompt:
    @${EDITOR:-vim} scripts/ralph/prompt.md

# --- INTERNAL ----------------------------------------------------------------

_setup-ralph:
    #!/usr/bin/env bash
    mkdir -p scripts/ralph
    
    # Create ralph.sh
    cat > scripts/ralph/ralph.sh << 'EOF'
#!/bin/bash
set -e
MAX=${1:-10}
DIR="$(cd "$(dirname "$0")" && pwd)"
PRD="$DIR/prd.json"

all_done() { [ "$(jq '[.userStories[] | select(.passes==false)] | length' "$PRD")" -eq 0 ]; }

for i in $(seq 1 $MAX); do
    all_done && echo "✅ Complete!" && exit 0
    NEXT=$(jq -r '[.userStories[] | select(.passes==false)] | sort_by(.priority) | .[0].title' "$PRD")
    echo "[$i/$MAX] $NEXT"
    cat "$DIR/prompt.md" | amp -x --dangerously-allow-all
done
echo "⚠️ Max iterations. Run 'just go' to continue."
EOF
    chmod +x scripts/ralph/ralph.sh
    
    # Create prompt.md
    if [ ! -f "scripts/ralph/prompt.md" ]; then
        cat > scripts/ralph/prompt.md << 'EOF'
# Ralph Iteration

1. Read scripts/ralph/prd.json - find highest priority story where passes: false
2. Read scripts/ralph/progress.txt - context from previous iterations
3. Read AGENTS.md - project conventions

Implement ONLY that one story. When done:
- Commit: "[Ralph] {id}: {title}"
- Update prd.json: set passes to true  
- Append learnings to progress.txt

If ALL stories complete, output: COMPLETE
EOF
    fi
    
    # Create progress.txt
    if [ ! -f "scripts/ralph/progress.txt" ]; then
        echo "# Progress Log" > scripts/ralph/progress.txt
    fi
