#!/usr/bin/env bash
set -euo pipefail

# Setup agentMemory MCP server for crushable-wingman.
#
# What this does:
# - Clones (or updates) webzler/agentMemory into ~/.codex/vendor_imports/agentMemory
# - Installs dependencies and compiles TypeScript
# - Registers an MCP server in Codex named "agentmemory-wingman"
#
# Customization via env vars:
# - AGENTMEMORY_INSTALL_DIR (default: ~/.codex/vendor_imports/agentMemory)
# - AGENTMEMORY_WORKSPACE_DIR (default: ~/.codex/state/crushable-wingman/agentmemory-workspace)
# - AGENTMEMORY_PROJECT_ID (default: crushable-wingman)
# - AGENTMEMORY_MCP_NAME (default: agentmemory-wingman)

INSTALL_DIR="${AGENTMEMORY_INSTALL_DIR:-$HOME/.codex/vendor_imports/agentMemory}"
WORKSPACE_DIR="${AGENTMEMORY_WORKSPACE_DIR:-$HOME/.codex/state/crushable-wingman/agentmemory-workspace}"
PROJECT_ID="${AGENTMEMORY_PROJECT_ID:-crushable-wingman}"
MCP_NAME="${AGENTMEMORY_MCP_NAME:-agentmemory-wingman}"

echo "== agentMemory install dir: $INSTALL_DIR"
echo "== agentMemory workspace dir: $WORKSPACE_DIR"
echo "== agentMemory project id: $PROJECT_ID"
echo "== Codex MCP name: $MCP_NAME"

mkdir -p "$(dirname "$INSTALL_DIR")"

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "== Updating repo"
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "== Cloning repo"
  git clone https://github.com/webzler/agentMemory "$INSTALL_DIR"
fi

echo "== Installing deps and compiling"
cd "$INSTALL_DIR"
npm install
npm run compile

SERVER_JS="$INSTALL_DIR/out/mcp-server/server.js"
if [ ! -f "$SERVER_JS" ]; then
  echo "[ERROR] MCP server entrypoint not found: $SERVER_JS" >&2
  echo "Try: cd \"$INSTALL_DIR\" && npm run compile" >&2
  exit 2
fi

echo "== Ensuring workspace dir"
mkdir -p "$WORKSPACE_DIR"

echo "== Registering MCP server in Codex"
codex mcp remove "$MCP_NAME" >/dev/null 2>&1 || true
codex mcp add "$MCP_NAME" -- node "$SERVER_JS" "$PROJECT_ID" "$WORKSPACE_DIR"

echo "== Done"
echo "Verify with: codex mcp list | rg -n \"$MCP_NAME\""

