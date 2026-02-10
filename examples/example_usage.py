#!/usr/bin/env python3
"""
Example usage of beaunifi utilities.
"""

from beaunifi.utils import (
    beautify_js,
    minify_js,
    beautify_css,
    minify_css,
    is_minified,
    smart_process,
)


def main():
    print("=" * 60)
    print("Beaunifi Example Usage")
    print("=" * 60)
    
    # Example 1: Working with minified JS
    print("\n1. Working with minified JavaScript:")
    print("-" * 60)
    
    minified_js = "function calculate(a,b){return a+b*2;}const result=calculate(5,3);"
    print(f"Original (minified): {minified_js[:50]}...")
    print(f"Is minified? {is_minified(minified_js, 'js')}")
    
    pretty_js = beautify_js(minified_js)
    print(f"\nBeautified:\n{pretty_js}")
    
    re_minified = minify_js(pretty_js)
    print(f"Re-minified: {re_minified}")
    
    # Example 2: Working with minified CSS
    print("\n2. Working with minified CSS:")
    print("-" * 60)
    
    minified_css = ".container{display:flex;flex-direction:column;gap:1rem;padding:20px}"
    print(f"Original (minified): {minified_css}")
    print(f"Is minified? {is_minified(minified_css, 'css')}")
    
    pretty_css = beautify_css(minified_css)
    print(f"\nBeautified:\n{pretty_css}")
    
    # Example 3: Smart process workflow
    print("\n3. Smart Process Workflow:")
    print("-" * 60)
    
    # Read mode - beautify for editing
    print("Action: 'read' - Beautify for editing")
    result = smart_process(minified_js, "js", action="read")
    print(f"  Was minified: {result['was_minified']}")
    print(f"  Code length: {result['original_length']} -> {result['final_length']}")
    
    # Edit mode - apply changes
    print("\nAction: 'edit' - Apply modifications")
    result = smart_process(
        minified_js,
        "js",
        action="edit",
        modifications='[{"find": "calculate", "replace": "compute"}]'
    )
    print(f"  Modified code:\n{result['code'][:100]}...")
    
    # Write mode - re-minify for production
    print("\nAction: 'write' - Re-minify for production")
    result = smart_process(
        minified_js,
        "js",
        action="write",
        modifications='[{"find": "calculate", "replace": "compute"}]'
    )
    print(f"  Final minified: {result['code']}")
    print(f"  Was re-minified: {result.get('was_re_minified', False)}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
