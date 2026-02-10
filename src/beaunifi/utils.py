"""
Utility functions for beautifying and minifying JS/CSS code.
Includes intelligent minification detection.
"""

import re
import json
from typing import Literal

import jsbeautifier
import cssbeautifier
import jsmin
import rcssmin


def beautify_js(code: str, indent_size: int = 2) -> str:
    """
    Beautify JavaScript code.
    
    Args:
        code: JavaScript code to beautify
        indent_size: Number of spaces for indentation
        
    Returns:
        Beautified JavaScript code
    """
    opts = jsbeautifier.default_options()
    opts.indent_size = indent_size
    opts.max_preserve_newlines = 2
    opts.preserve_newlines = True
    opts.keep_array_indentation = False
    opts.break_chained_methods = False
    opts.indent_scripts = "normal"
    opts.brace_style = "collapse"
    opts.space_before_conditional = True
    opts.unescape_strings = False
    opts.jslint_happy = False
    opts.end_with_newline = True
    opts.wrap_line_length = 0
    opts.indent_inner_html = False
    opts.comma_first = False
    opts.e4x = False
    opts.indent_empty_lines = False
    
    return jsbeautifier.beautify(code, opts)


def minify_js(code: str) -> str:
    """
    Minify JavaScript code.
    
    Args:
        code: JavaScript code to minify
        
    Returns:
        Minified JavaScript code
    """
    return jsmin.jsmin(code)


def beautify_css(code: str, indent_size: int = 2) -> str:
    """
    Beautify CSS code.
    
    Args:
        code: CSS code to beautify
        indent_size: Number of spaces for indentation
        
    Returns:
        Beautified CSS code
    """
    opts = cssbeautifier.default_options()
    opts.indent_size = indent_size
    opts.max_preserve_newlines = 2
    opts.preserve_newlines = True
    opts.newline_between_rules = True
    opts.end_with_newline = True
    opts.indent_with_tabs = False
    opts.selector_separator_newline = True
    
    return cssbeautifier.beautify(code, opts)


def minify_css(code: str) -> str:
    """
    Minify CSS code.
    
    Args:
        code: CSS code to minify
        
    Returns:
        Minified CSS code
    """
    return rcssmin.cssmin(code)


def is_minified(code: str, file_type: Literal["js", "css"]) -> bool:
    """
    Detect if code appears to be minified.
    
    Uses heuristics based on:
    - Average line length
    - Ratio of newlines to content
    - Presence of meaningful indentation
    - Minification patterns (no spaces after keywords/punctuation)
    
    Args:
        code: Code to check
        file_type: Type of code (js or css)
        
    Returns:
        True if code appears minified, False otherwise
    """
    if not code or not code.strip():
        return False
    
    lines = code.split('\n')
    total_lines = len(lines)
    content_length = len(code)
    
    # Single line with any code is likely minified
    if total_lines == 1 and len(code.strip()) > 10:
        return True
    
    # Calculate average line length
    non_empty_lines = [line for line in lines if line.strip()]
    if not non_empty_lines:
        return False
    
    avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
    
    # Very long average lines suggest minification
    if avg_line_length > 200:
        return True
    
    # Check for minimal newlines relative to content length
    newline_ratio = total_lines / content_length
    
    # Minified code has very few newlines relative to content
    if content_length > 500 and newline_ratio < 0.01:
        return True
    
    # Check for meaningful indentation in non-minified code
    indented_lines = sum(
        1 for line in lines 
        if line.startswith('  ') or line.startswith('\t')
    )
    
    # If we have many lines but very little indentation, likely minified
    if total_lines > 10 and indented_lines < total_lines * 0.1:
        if avg_line_length > 100:
            return True
    
    # File type specific checks
    if file_type == "js":
        # Check for patterns common in minified JS
        # No spaces after keywords like function, var, let, const, if, for, while
        patterns = [
            r'function\w*\(',
            r'var\w',
            r'let\w',
            r'const\w',
            r'if\(',
            r'for\(',
            r'while\(',
            r'else\{',
            r'\}\w',  # closing brace followed immediately by word
        ]
        minified_patterns = sum(1 for pattern in patterns if re.search(pattern, code))
        
        # Check for lack of spaces after commas (common in minified code)
        comma_without_space = len(re.findall(r',[^\s]', code))
        comma_with_space = len(re.findall(r',\s', code))
        
        # If there are more commas without space than with, likely minified
        if comma_without_space > comma_with_space and comma_without_space > 1:
            minified_patterns += 2
        
        # Low threshold for minified pattern detection
        if minified_patterns >= 2:
            return True
            
    elif file_type == "css":
        # Check for patterns common in minified CSS
        # No space after colon or semicolon
        colon_without_space = len(re.findall(r':[^\s]', code))
        semicolon_without_space = len(re.findall(r';[^\s]', code))
        
        # If we have these patterns and reasonable length, likely minified
        if (colon_without_space > 0 or semicolon_without_space > 0) and avg_line_length > 30:
            return True
    
    return False


def smart_process(
    code: str,
    file_type: Literal["js", "css"],
    action: Literal["read", "edit", "write"] = "read",
    modifications: str | None = None,
    indent_size: int = 2,
) -> dict:
    """
    Smart workflow for processing code:
    1. Detect if code is minified
    2. Beautify if minified
    3. Perform requested action
    4. Re-minify if original was minified
    
    Args:
        code: Code to process
        file_type: Type of code (js or css)
        action: Action to perform - 'read', 'edit', or 'write'
        modifications: JSON string of modifications for 'edit' action
                      Format: [{"find": "text", "replace": "new_text"}]
        indent_size: Indentation size for beautification
        
    Returns:
        Dictionary with processing results
    """
    result = {
        "was_minified": False,
        "was_beautified": False,
        "action": action,
        "file_type": file_type,
        "original_length": len(code),
        "final_length": 0,
        "code": "",
        "message": "",
    }
    
    # Step 1: Detect if minified
    minified = is_minified(code, file_type)
    result["was_minified"] = minified
    
    working_code = code
    
    # Step 2: Beautify if minified
    if minified:
        if file_type == "js":
            working_code = beautify_js(code, indent_size)
        else:  # css
            working_code = beautify_css(code, indent_size)
        result["was_beautified"] = True
        result["beautified_length"] = len(working_code)
    
    # Step 3: Perform action
    if action == "read":
        # Just return beautified code for reading/editing
        result["code"] = working_code
        result["message"] = "Code beautified for reading. Edit and use 'write' action to get minified result."
        result["final_length"] = len(working_code)
        
    elif action == "edit":
        # Apply modifications (first on original, then beautify if needed)
        working_code = code  # Start with original code
        
        if modifications:
            try:
                mods = json.loads(modifications)
                if isinstance(mods, list):
                    for mod in mods:
                        find_text = mod.get("find", "")
                        replace_text = mod.get("replace", "")
                        working_code = working_code.replace(find_text, replace_text)
                    result["modifications_applied"] = len(mods)
                else:
                    result["error"] = "Modifications must be a list"
            except json.JSONDecodeError as e:
                result["error"] = f"Invalid modifications JSON: {str(e)}"
        
        # Now beautify the modified code
        if file_type == "js":
            working_code = beautify_js(working_code, indent_size)
        else:  # css
            working_code = beautify_css(working_code, indent_size)
        
        result["code"] = working_code
        result["message"] = "Modifications applied. Use 'write' action to get minified result."
        result["final_length"] = len(working_code)
        
    elif action == "write":
        # Apply modifications if any, then minify
        if modifications:
            try:
                mods = json.loads(modifications)
                if isinstance(mods, list):
                    for mod in mods:
                        find_text = mod.get("find", "")
                        replace_text = mod.get("replace", "")
                        working_code = working_code.replace(find_text, replace_text)
            except json.JSONDecodeError:
                pass  # Ignore modification errors on write
        
        # Minify if original was minified
        if minified:
            if file_type == "js":
                working_code = minify_js(working_code)
            else:  # css
                working_code = minify_css(working_code)
            result["was_re_minified"] = True
        
        result["code"] = working_code
        result["final_length"] = len(working_code)
        result["message"] = "Code processed and minified for production."
    
    return result


def get_file_type_from_extension(filename: str) -> Literal["js", "css", "unknown"]:
    """
    Determine file type from filename extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        File type: 'js', 'css', or 'unknown'
    """
    if filename.lower().endswith(('.js', '.jsx', '.mjs', '.cjs')):
        return "js"
    elif filename.lower().endswith(('.css', '.scss', '.sass', '.less')):
        return "css"
    return "unknown"
