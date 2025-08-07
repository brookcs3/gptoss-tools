#!/usr/bin/env python3
"""
GPT OSS TUI Launcher
Quick launcher for the Claude Code-style interface
"""

import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking GPT OSS TUI requirements...")
    
    # Check if Ollama is running
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is running")
            
            # Check for GPT OSS model
            if "gpt-oss" in result.stdout.decode():
                print("✅ GPT OSS model available")
            else:
                print("⚠️  GPT OSS model not found. Run: ollama pull gpt-oss:20b")
        else:
            print("❌ Ollama not running. Start with: ollama serve")
            return False
    except Exception:
        print("❌ Ollama not found. Install from: https://ollama.ai")
        return False
    
    # Check tools
    tools_dir = Path(__file__).parent
    tools = ["glop", "grep", "search", "read", "readymyfiles"]
    
    for tool in tools:
        if (tools_dir / tool).exists():
            print(f"✅ {tool} tool ready")
        else:
            print(f"❌ {tool} tool missing")
            return False
    
    print("\n🚀 All requirements met! Launching GPT OSS TUI...")
    return True

def main():
    """Launch the GPT OSS TUI"""
    print("🤖 GPT OSS TUI Launcher")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Please fix the issues above before launching.")
        sys.exit(1)
    
    # Set terminal environment
    os.environ["TERM"] = "xterm-256color"
    os.environ["COLORTERM"] = "truecolor"
    
    # Launch the TUI
    try:
        subprocess.run([sys.executable, "gpt_oss_tui.py"], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using GPT OSS!")
    except Exception as e:
        print(f"\n❌ Error launching TUI: {e}")

if __name__ == "__main__":
    main()
