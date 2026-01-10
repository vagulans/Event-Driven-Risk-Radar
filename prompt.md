# Ralph Iteration

1. Read scripts/ralph/prd.json - find highest priority story where passes: false
2. Read scripts/ralph/progress.txt - context from previous iterations
3. Read AGENTS.md - project conventions

Implement ONLY that one story. When done:
- Commit: "[Ralph] {id}: {title}"
- Update prd.json: set passes to true  
- Append learnings to progress.txt

If ALL stories complete, output: COMPLETE
