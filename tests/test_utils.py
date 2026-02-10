#!/usr/bin/env python3
"""
Test utilities for beaunifi.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beaunifi.utils import (
    beautify_js,
    minify_js,
    beautify_css,
    minify_css,
    is_minified,
    smart_process,
    get_file_type_from_extension,
)


def test_js_beautify_minify():
    """Test JS beautify and minify roundtrip."""
    print("Testing JS beautify/minify...")
    
    # Minified JS
    minified = "function test(){var a=1;return a+2}"
    
    # Should detect as minified
    assert is_minified(minified, "js"), "Should detect minified JS"
    
    # Beautify
    pretty = beautify_js(minified)
    assert "\n" in pretty, "Beautified JS should have newlines"
    assert "    " in pretty or "  " in pretty, "Beautified JS should have indentation"
    
    # Minify again
    re_minified = minify_js(pretty)
    assert "\n" not in re_minified.strip(), "Minified JS should not have newlines"
    
    print("  ✓ JS beautify/minify works")


def test_css_beautify_minify():
    """Test CSS beautify and minify roundtrip."""
    print("Testing CSS beautify/minify...")
    
    # Minified CSS
    minified = ".class{color:red;margin:0;padding:10px}"
    
    # Should detect as minified
    assert is_minified(minified, "css"), "Should detect minified CSS"
    
    # Beautify
    pretty = beautify_css(minified)
    assert "\n" in pretty, "Beautified CSS should have newlines"
    
    # Minify again
    re_minified = minify_css(pretty)
    assert "\n" not in re_minified.strip(), "Minified CSS should not have newlines"
    
    print("  ✓ CSS beautify/minify works")


def test_is_minified_detection():
    """Test minification detection."""
    print("Testing minification detection...")
    
    # Minified examples
    assert is_minified("function test(){return 1}", "js")
    assert is_minified(".a{color:red}", "css")
    
    # Beautified examples (should NOT be detected as minified)
    pretty_js = """function test() {
    return 1;
}"""
    assert not is_minified(pretty_js, "js"), "Should not detect pretty JS as minified"
    
    pretty_css = """.class {
    color: red;
}"""
    assert not is_minified(pretty_css, "css"), "Should not detect pretty CSS as minified"
    
    print("  ✓ Minification detection works")


def test_smart_process():
    """Test smart process workflow."""
    print("Testing smart process...")
    
    minified_js = "function test(){var a=1;return a}"
    
    # Read action - should beautify
    result = smart_process(minified_js, "js", action="read")
    assert result["was_minified"] == True
    assert result["was_beautified"] == True
    assert "\n" in result["code"]
    
    # Write action - should re-minify
    result = smart_process(minified_js, "js", action="write")
    assert result["was_re_minified"] == True
    assert "\n" not in result["code"].strip()
    
    # Edit action with modifications
    result = smart_process(
        minified_js,
        "js",
        action="edit",
        modifications='[{"find": "var a=1", "replace": "var b=2"}]'
    )
    assert "var b = 2" in result["code"]
    
    print("  ✓ Smart process works")


def test_file_type_detection():
    """Test file type detection from extension."""
    print("Testing file type detection...")
    
    assert get_file_type_from_extension("test.js") == "js"
    assert get_file_type_from_extension("test.jsx") == "js"
    assert get_file_type_from_extension("test.mjs") == "js"
    assert get_file_type_from_extension("test.css") == "css"
    assert get_file_type_from_extension("test.scss") == "css"
    assert get_file_type_from_extension("test.txt") == "unknown"
    
    print("  ✓ File type detection works")


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running Beaunifi Tests")
    print("=" * 50)
    print()
    
    try:
        test_js_beautify_minify()
        test_css_beautify_minify()
        test_is_minified_detection()
        test_smart_process()
        test_file_type_detection()
        
        print()
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 50)
        print(f"Test failed: {e}")
        print("=" * 50)
        return 1
    except Exception as e:
        print()
        print("=" * 50)
        print(f"Error: {e}")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
