# PRD Converter Skill

Convert a markdown PRD into Ralph-compatible `prd.json` format with atomic user stories.

## Output Format

Create `scripts/ralph/prd.json` with this exact structure:

```json
{
  "project": "Project Name",
  "branchName": "ralph/project-name-kebab-case",
  "description": "One-line description from PRD",
  "userStories": [
    {
      "id": "US-001",
      "title": "Short descriptive title",
      "description": "As a developer, I need X so that Y.",
      "acceptanceCriteria": [
        "Specific, testable criterion 1",
        "Specific, testable criterion 2",
        "All tests pass"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Conversion Rules

### 1. Story Sizing (CRITICAL)

Each story must complete in ONE Amp context window. This is the most important rule.

**Right-sized stories:**
- Create single file with 1-3 classes
- Implement one API endpoint
- Add one CLI command
- Write tests for one module
- Create configuration file

**Too big (MUST split):**
- "Build entire module" → Split into file-per-story
- "Add authentication" → Split: model, routes, middleware, tests
- "Create API" → Split: one endpoint per story

### 2. Story Extraction

From PRD sections, extract stories like this:

| PRD Section | Stories |
|------------|---------|
| Module with 5 files | 5 stories (one per file) |
| Class with many methods | 1-2 stories (setup + implementation) |
| Configuration section | 1 story for config files |
| Entry point | 1 story |

### 3. Priority Assignment

```
Priority 1-2:   Project setup, core data structures
Priority 3-5:   Foundation modules (config, models, utils)
Priority 6-10:  Core functionality modules
Priority 11-15: Integration, glue code
Priority 16-20: Polish, documentation, tests
Priority 99:    Final integration story (always last)
```

### 4. Acceptance Criteria Rules

- Must be **testable** (can verify pass/fail)
- Must be **specific** (not "works correctly")
- Include "All tests pass" for code stories
- Include "File imports without errors" for new files
- Include "Types check (mypy)" for Python with types

**Good criteria:**
- "Create `websocket_client.py` with `BinanceWS` class"
- "Implement `connect()`, `subscribe()`, `on_message()` methods"
- "Add auto-reconnect with exponential backoff (1s, 2s, 4s...)"
- "All imports resolve correctly"

**Bad criteria:**
- "Implement websocket stuff"
- "Make it work"
- "Handle errors properly"

### 5. Always Include These Stories

**First story (priority 1):**
```json
{
  "id": "US-001",
  "title": "Initialize project structure",
  "description": "As a developer, I need the project scaffolding.",
  "acceptanceCriteria": [
    "Create directory structure from PRD",
    "Create requirements.txt with all dependencies",
    "Create main.py entry point (empty shell)",
    "Create all __init__.py files",
    "Project imports without errors"
  ],
  "priority": 1,
  "passes": false,
  "notes": ""
}
```

**Last story (priority 99):**
```json
{
  "id": "US-XXX",
  "title": "Final integration and testing",
  "description": "As a developer, I need to verify everything works together.",
  "acceptanceCriteria": [
    "All modules import from main.py",
    "Entry point runs without errors",
    "All type hints pass mypy",
    "README is complete"
  ],
  "priority": 99,
  "passes": false,
  "notes": ""
}
```

## Example Conversion

### Input PRD snippet:
```markdown
## Module 1: Data Ingestion (`ingest/`)

**Files:**
- `websocket_client.py` - Binance WS connection
- `normalizers.py` - Data normalization
- `publisher.py` - Redis publisher

**Key Classes:**
- `BinanceOptionsWS` - WebSocket manager
- `NormalizedOption` - Standardized option data
```

### Output stories:
```json
{
  "userStories": [
    {
      "id": "US-002",
      "title": "Create ingest/websocket_client.py",
      "description": "As a developer, I need WebSocket connectivity to Binance.",
      "acceptanceCriteria": [
        "Create ingest/websocket_client.py",
        "Implement BinanceOptionsWS class",
        "Add connect(), subscribe(), on_message() methods",
        "Add auto-reconnect logic",
        "File imports correctly"
      ],
      "priority": 3,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-003",
      "title": "Create ingest/normalizers.py",
      "description": "As a developer, I need to normalize raw option data.",
      "acceptanceCriteria": [
        "Create ingest/normalizers.py",
        "Implement NormalizedOption dataclass",
        "Add normalization functions",
        "Include type hints",
        "File imports correctly"
      ],
      "priority": 4,
      "passes": false,
      "notes": ""
    },
    {
      "id": "US-004",
      "title": "Create ingest/publisher.py",
      "description": "As a developer, I need to publish data to Redis.",
      "acceptanceCriteria": [
        "Create ingest/publisher.py",
        "Implement RedisPublisher class",
        "Add publish() method for normalized data",
        "File imports correctly"
      ],
      "priority": 5,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Critical Reminders

1. **One file = One story** (usually)
2. **Stories must be atomic** - completable in one context
3. **Criteria must be verifiable** - no vague language
4. **Priority determines order** - dependencies first
5. **Always end with integration story** - priority 99
