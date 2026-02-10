#!/usr/bin/env python3
"""
Beaunifi MCP Server
A Model Context Protocol server for beautifying and minifying JS/CSS files.
"""

import asyncio
import json
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
import mcp.types as types

from .utils import (
    beautify_js,
    beautify_css,
    minify_js,
    minify_css,
    is_minified,
    smart_process,
)

# Server instance
server = Server("beaunifi")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="beaunifi://docs",
            name="Beaunifi Documentation",
            description="Documentation for the Beaunifi MCP server",
            mimeType="text/plain",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: Any) -> str:
    """Read a resource by URI."""
    if str(uri) == "beaunifi://docs":
        return """
# Beaunifi MCP Server

Available tools:
- beautify_js: Beautify JavaScript code
- beautify_css: Beautify CSS code
- minify_js: Minify JavaScript code
- minify_css: Minify CSS code
- is_minified: Check if code appears to be minified
- smart_process: Smart workflow - auto-detect, beautify if needed, process, re-minify

Use smart_process for the best experience when working with unknown files.
"""
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="beautify_js",
            description="Beautify JavaScript code to make it readable",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "JavaScript code to beautify",
                    },
                    "indent_size": {
                        "type": "integer",
                        "description": "Number of spaces for indentation",
                        "default": 2,
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="minify_js",
            description="Minify JavaScript code for production",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "JavaScript code to minify",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="beautify_css",
            description="Beautify CSS code to make it readable",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CSS code to beautify",
                    },
                    "indent_size": {
                        "type": "integer",
                        "description": "Number of spaces for indentation",
                        "default": 2,
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="minify_css",
            description="Minify CSS code for production",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "CSS code to minify",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="is_minified",
            description="Check if code appears to be minified based on line length and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to check",
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["js", "css"],
                        "description": "Type of code (js or css)",
                    },
                },
                "required": ["code", "file_type"],
            },
        ),
        Tool(
            name="smart_process",
            description="Smart workflow: auto-detect if minified, beautify if needed, process, and optionally re-minify. Perfect for editing minified files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to process",
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["js", "css"],
                        "description": "Type of code (js or css)",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["read", "edit", "write"],
                        "description": "Action to perform: 'read' returns beautified code, 'edit' applies modifications, 'write' returns minified result",
                        "default": "read",
                    },
                    "modifications": {
                        "type": "string",
                        "description": "JSON string describing modifications to apply (for 'edit' action). Format: [{\"find\": \"text\", \"replace\": \"new_text\"}]",
                    },
                    "indent_size": {
                        "type": "integer",
                        "description": "Number of spaces for indentation when beautifying",
                        "default": 2,
                    },
                },
                "required": ["code", "file_type"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}

    try:
        if name == "beautify_js":
            code = arguments.get("code", "")
            indent_size = arguments.get("indent_size", 2)
            result = beautify_js(code, indent_size)
            return [
                TextContent(
                    type="text",
                    text=result,
                )
            ]

        elif name == "minify_js":
            code = arguments.get("code", "")
            result = minify_js(code)
            return [
                TextContent(
                    type="text",
                    text=result,
                )
            ]

        elif name == "beautify_css":
            code = arguments.get("code", "")
            indent_size = arguments.get("indent_size", 2)
            result = beautify_css(code, indent_size)
            return [
                TextContent(
                    type="text",
                    text=result,
                )
            ]

        elif name == "minify_css":
            code = arguments.get("code", "")
            result = minify_css(code)
            return [
                TextContent(
                    type="text",
                    text=result,
                )
            ]

        elif name == "is_minified":
            code = arguments.get("code", "")
            file_type = arguments.get("file_type", "js")
            result = is_minified(code, file_type)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "is_minified": result,
                            "message": f"Code appears to be {'minified' if result else 'beautified/normal'}",
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "smart_process":
            code = arguments.get("code", "")
            file_type = arguments.get("file_type", "js")
            action = arguments.get("action", "read")
            modifications = arguments.get("modifications")
            indent_size = arguments.get("indent_size", 2)

            result = smart_process(
                code=code,
                file_type=file_type,
                action=action,
                modifications=modifications,
                indent_size=indent_size,
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": str(e), "tool": name}, indent=2
                ),
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="beaunifi",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
