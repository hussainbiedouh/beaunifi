# Beaunifi

An MCP (Model Context Protocol) server that intelligently beautifies and minifies JavaScript and CSS files. It can detect if a file is minified and automatically beautify it before processing, then re-minify it afterward.

## Features

- 🔧 **Beautify** JS/CSS code for easier editing
- 📦 **Minify** JS/CSS code for production
- 🧠 **Auto-detect** minified files and handle them intelligently
- 🔁 **Workflow mode**: Beautify → Edit → Minify (automatic)
- 🔌 **MCP Compatible**: Works with Claude Code, Cursor, Antigravity, and more

## Installation

### Using UV (Recommended)

```bash
# Navigate to the project directory
cd E:\Projects\OSP\beaunifi

# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install -e .
```

## MCP Configuration

### Claude Code

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "beaunifi": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "python",
        "-m",
        "beaunifi.server"
      ],
      "cwd": "E:\\Projects\\OSP\\beaunifi"
    }
  }
}
```

Or use the provided config file:
```bash
# Copy the config to Claude Code directory
cp mcp-configs/claude-code.json ~/.claude/mcp-servers/beaunifi.json
```

### Cursor

Add to your Cursor settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "beaunifi": {
      "command": "uv",
      "args": [
        "run",
        "--python",
        "python",
        "-m",
        "beaunifi.server"
      ],
      "cwd": "E:\\Projects\\OSP\\beaunifi"
    }
  }
}
```

### Antigravity

Add to your Antigravity MCP config:

```json
{
  "name": "beaunifi",
  "transport": {
    "type": "stdio",
    "command": "uv",
    "args": ["run", "--python", "python", "-m", "beaunifi.server"],
    "cwd": "E:\\Projects\\OSP\\beaunifi"
  }
}
```

## Available Tools

### 1. `beautify_js`
Beautify JavaScript code

**Parameters:**
- `code` (string): JavaScript code to beautify
- `indent_size` (number, optional): Indentation size (default: 2)

### 2. `minify_js`
Minify JavaScript code

**Parameters:**
- `code` (string): JavaScript code to minify

### 3. `beautify_css`
Beautify CSS code

**Parameters:**
- `code` (string): CSS code to beautify
- `indent_size` (number, optional): Indentation size (default: 2)

### 4. `minify_css`
Minify CSS code

**Parameters:**
- `code` (string): CSS code to minify

### 5. `is_minified`
Check if code appears to be minified

**Parameters:**
- `code` (string): Code to check
- `file_type` (string): Either "js" or "css"

### 6. `smart_process`
Smart workflow: auto-detect minification, beautify if needed, and re-minify

**Parameters:**
- `code` (string): Code to process
- `file_type` (string): Either "js" or "css"
- `action` (string): Action to perform ("read", "edit", or "write")
- `modifications` (string, optional): Modifications to apply (for "edit" action)

## Usage Examples

### Direct Python Usage

```python
from beaunifi.utils import beautify_js, minify_js, is_minified

# Check if code is minified
code = "function test(){return 1}"
if is_minified(code, "js"):
    pretty = beautify_js(code)
    # ... make edits ...
    final = minify_js(pretty)
```

### MCP Tool Usage

When using with an MCP client:

```
"Please beautify this minified JS file: [code]"
"Minify this CSS for production: [code]"
"Smart process this file - detect if minified and handle appropriately: [code]"
```

## Smart Process Workflow

The `smart_process` tool provides an intelligent workflow:

1. **Detect** if the code is minified
2. **Beautify** if minified (for easier editing)
3. **Perform** the requested action (read/edit)
4. **Re-minify** if the original was minified

This is perfect for AI assistants that need to edit minified files without losing the minification.

## Development

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy src/beaunifi

# Linting
uv run ruff check src/beaunifi
```

## License

MIT
