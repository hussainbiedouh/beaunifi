#!/bin/bash
set -e

echo "=========================================="
echo "Beaunifi MCP Server Setup"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "[ERROR] UV is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
uv venv

echo "[2/4] Installing dependencies..."
uv pip install -e ".[dev]"

echo "[3/4] Verifying installation..."
uv run python -c "from beaunifi.utils import beautify_js, minify_js, is_minified; print('✓ Imports successful')"

echo "[4/4] Running tests..."
uv run python tests/test_utils.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To start the MCP server, run:"
echo "  uv run python -m beaunifi.server"
echo ""
echo "To use with Claude Code, add to settings:"
echo "  Copy mcp-configs/claude-code.json to your Claude config"
echo ""
