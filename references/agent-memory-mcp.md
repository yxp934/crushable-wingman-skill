# MCP External Memory (agentMemory) Integration

Use this when you want cross-session "external memory" with search and structured storage, instead of copy/pasting a case file.

This uses the `agentMemory` MCP server (same tooling referenced by `agent-memory-mcp` on skills.sh).

## What You Get

- Persistent memory across sessions
- Search (`memory_search`) to recall context quickly
- Read/write/update tools to keep a single source of truth

## Setup (Codex)

### 1) Install agentMemory code locally

Pick an install directory (recommended):
- `~/.codex/vendor_imports/agentMemory`

Clone and build:
```bash
mkdir -p ~/.codex/vendor_imports
cd ~/.codex/vendor_imports
git clone https://github.com/webzler/agentMemory agentMemory
cd agentMemory
npm install
npm run compile
```

### 2) Register the MCP server in Codex

Decide where you want the memory workspace to live (recommended, outside git repos):
- `~/.codex/state/crushable-wingman/agentmemory-workspace`

Register:
```bash
mkdir -p ~/.codex/state/crushable-wingman/agentmemory-workspace
codex mcp remove agentmemory-wingman || true
codex mcp add agentmemory-wingman -- node \
  ~/.codex/vendor_imports/agentMemory/out/mcp-server/server.js \
  crushable-wingman \
  ~/.codex/state/crushable-wingman/agentmemory-workspace
```

After this, Codex should have MCP tools like:
- `memory_search`
- `memory_read`
- `memory_write`
- `memory_list`
- `memory_update` (if supported)
- `memory_stats`

## Conventions For This Wingman Skill

### Keys and Tags

Store one case file per person as a single memory entry:
- Key: `wingman/case-file/<handle>`
- Type: `wingman_case_file`
- Tags:
  - `wingman`
  - `case-file`
  - `crush:<handle>`

Example handle: `alex-work` (stable, short, unique).

### Read on Start

At the start of a conversation:
1. If the user provides a handle, `memory_read` that key.
2. If the user provides only a name, `memory_search` for `crush:<handle>` or name text to find the best match.
3. If nothing exists, create a new case file from `references/case-file-template.md` and `memory_write` it.

### Update at Checkpoints

At checkpoints (intake complete, new stable info, user asks "summarize"):
1. Update the case file text.
2. Persist it with `memory_update` (preferred) or `memory_write` (overwrite) using the same key.

### Search During Coaching

Use `memory_search` for retrieval when the user asks something like:
- "What do you remember about her?"
- "What are her boundaries?"
- "What should I avoid?"

Search queries should be short and specific (one intent per query).
