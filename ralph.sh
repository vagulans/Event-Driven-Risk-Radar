#!/bin/bash
set -e

MAX=${1:-10}
DIR="$(cd "$(dirname "$0")" && pwd)"
PRD="$DIR/prd.json"

all_done() { 
    [ "$(jq '[.userStories[] | select(.passes==false)] | length' "$PRD")" -eq 0 ]
}

for i in $(seq 1 $MAX); do
    all_done && echo "✅ Complete!" && exit 0
    NEXT=$(jq -r '[.userStories[] | select(.passes==false)] | sort_by(.priority) | .[0].title' "$PRD")
    echo "[$i/$MAX] $NEXT"
    cat "$DIR/prompt.md" | amp -x --dangerously-allow-all
done

echo "⚠️ Max iterations. Run 'just go' to continue."
