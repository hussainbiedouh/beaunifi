@echo off
echo ==========================================
echo Beaunifi MCP Server Setup
echo ==========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] UV is not installed. Please install it first:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    exit /b 1
)

echo [1/4] Creating virtual environment...
uv venv

echo [2/4] Installing dependencies...
uv pip install -e ".[dev]"

echo [3/4] Verifying installation...
uv run python -c "from beaunifi.utils import beautify_js, minify_js, is_minified; print('✓ Imports successful')"

echo [4/4] Running tests...
uv run python tests/test_utils.py

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To start the MCP server, run:
echo   uv run python -m beaunifi.server
echo.
echo To use with Claude Code, add to settings:
echo   Copy mcp-configs\claude-code.json to your Claude config
echo.
