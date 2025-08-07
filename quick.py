#!/usr/bin/env python3
"""
Quick GPT OSS Commands - One-line interface
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run GPT OSS command with pretty output"""
    tools_dir = Path(__file__).parent
    result = subprocess.run(cmd, shell=True, cwd=tools_dir, capture_output=True, text=True)
    
    print(f"🤖 Running: {cmd}")
    print("─" * 50)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    print("─" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
🤖 GPT OSS Quick Commands

Usage: python3 quick.py <command>

Available commands:
  status     - Show system status with Rich UI
  files      - Find all Python files
  search     - Search for 'class' in code
  read       - Read a config file
  index      - Build search index
  dashboard  - Rich dashboard view
  
Examples:
  python3 quick.py status
  python3 quick.py files
  python3 quick.py dashboard
        """)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    commands = {
        'status': 'python3 gptoss_rich.py status',
        'files': './glop "*.py" --recursive',
        'search': './search "class"',
        'read': './read config.yaml',
        'index': './search index',
        'dashboard': 'python3 gptoss_rich.py status',
        'help': 'python3 gptoss_rich.py --help'
    }
    
    if cmd in commands:
        run_command(commands[cmd])
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'python3 quick.py' for help")
