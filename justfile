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

init: _check-deps _install-skills _init-git
    @echo ""
    @echo "✅ Auto-Ralph ready!"
    @echo "Next: just new 'your idea' OR just convert YOUR_PRD.md"

_check-deps:
    #!/usr/bin/env bash
    echo "🔍 Checking dependencies..."
    command -v amp >/dev/null || { echo "❌ amp CLI not found"; exit 1; }
    command -v jq >/dev/null || { echo "❌ jq not found"; exit 1; }
    echo "✅ Dependencies OK"

_install-skills:
    #!/usr/bin/env bash
    echo "📦 Installing Amp skills..."
    mkdir -p "${HOME}/.config/amp/skills"
    cp -r skills/* "${HOME}/.config/amp/skills/" 2>/dev/null || true
    echo "✅ Skills installed"

_init-git:
    #!/usr/bin/env bash
    [ ! -d ".git" ] && git init --quiet && git add -A && git commit -m "Initial" --quiet 2>/dev/null || true

# --- PROJECT CREATION --------------------------------------------------------

new idea:
    #!/usr/bin/env bash
    echo "🧠 Generating PRD..."
    echo "Load the prd-generator skill. Create a detailed PRD for: {{idea}}. Save to prd.md" | amp -x --dangerously-allow-all
    [ -f "prd.md" ] && echo "✅ Created prd.md - Next: just convert prd.md"

convert prd_file:
    #!/usr/bin/env bash
    [ ! -f "{{prd_file}}" ] && echo "❌ File not found: {{prd_file}}" && exit 1
    mkdir -p scripts/ralph
    echo "🔄 Converting PRD..."
    echo "Load the prd-converter skill. Convert {{prd_file}} to scripts/ralph/prd.json" | amp -x --dangerously-allow-all
    
    # Create ralph.sh
    cat > scripts/ralph/ralph.sh << 'RALPH_EOF'
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
    RALPH_EOF
    chmod +x scripts/ralph/ralph.sh
    
    # Create prompt.md
    cat > scripts/ralph/prompt.md << 'PROMPT_EOF'
    # Ralph Iteration
    1. Read scripts/ralph/prd.json - find highest priority story where passes: false
    2. Read scripts/ralph/progress.txt - context from previous iterations
    3. Read AGENTS.md - project conventions
    Implement ONLY that one story. When done:
    - Commit: "[Ralph] {id}: {title}"
    - Update prd.json: set passes to true  
    - Append learnings to progress.txt
    If ALL stories complete, output: COMPLETE
    PROMPT_EOF
    
    [ -f "scripts/ralph/prd.json" ] && echo "✅ Converted! Next: just go"

# --- RALPH EXECUTION ---------------------------------------------------------

go iterations="10":
    #!/usr/bin/env bash
    [ ! -f "scripts/ralph/prd.json" ] && echo "❌ No prd.json. Run: just convert YOUR_PRD.md" && exit 1
    [ ! -f "scripts/ralph/progress.txt" ] && echo "# Progress Log" > scripts/ralph/progress.txt
    echo "🚀 Starting Ralph ({{iterations}} iterations)"
    chmod +x scripts/ralph/ralph.sh
    scripts/ralph/ralph.sh {{iterations}}

step:
    @just go 1

# --- STATUS ------------------------------------------------------------------

status:
    #!/usr/bin/env bash
    [ ! -f "scripts/ralph/prd.json" ] && echo "No project yet" && exit 0
    echo "📊 $(jq -r '.project' scripts/ralph/prd.json)"
    TOTAL=$(jq '.userStories | length' scripts/ralph/prd.json)
    DONE=$(jq '[.userStories[] | select(.passes == true)] | length' scripts/ralph/prd.json)
    echo "Progress: $DONE / $TOTAL"
    jq -r '.userStories[] | (if .passes then "  ✅" else "  ⬜" end) + " [" + .id + "] " + .title' scripts/ralph/prd.json

log:
    @tail -50 scripts/ralph/progress.txt 2>/dev/null || echo "No progress yet"

# --- MAINTENANCE -------------------------------------------------------------

reset:
    #!/usr/bin/env bash
    [ -f "scripts/ralph/prd.json" ] && mkdir -p archive && mv scripts/ralph/prd.json scripts/ralph/progress.txt archive/ 2>/dev/null
    echo "✅ Reset"

edit-prd:
    @${EDITOR:-vim} scripts/ralph/prd.json

edit-prompt:
    @${EDITOR:-vim} scripts/ralph/prompt.md
