#!/usr/bin/env python3
"""
Quick test script for GPT OSS Tools
"""

import sys
import subprocess
from pathlib import Path

def run_test(tool_name, args, description):
    """Run a test command and report results"""
    print(f"Testing {tool_name}: {description}")
    
    try:
        result = subprocess.run(
            [f"./{tool_name}"] + args,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ {tool_name} working")
            return True
        else:
            print(f"  ❌ {tool_name} failed: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ {tool_name} timed out")
        return False
    except Exception as e:
        print(f"  ❌ {tool_name} error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing GPT OSS Tools\\n")
    
    tools_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        # Change to tools directory
        import os
        os.chdir(tools_dir)
        
        tests = [
            ("glop", ["--help"], "help command"),
            ("grep", ["--help"], "help command"),
            ("filewrite", ["templates"], "list templates"),
            ("read", ["--help"], "help command"),
            ("search", ["stats"], "show stats"),
            ("readymyfiles", ["--help"], "help command"),
        ]
        
        passed = 0
        total = len(tests)
        
        for tool, args, desc in tests:
            if run_test(tool, args, desc):
                passed += 1
        
        print(f"\\n📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed")
            return 1
            
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(main())
