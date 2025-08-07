#!/usr/bin/env python3
"""
External File Read Tool - Test implementation
Uses OpenAI SDK to call GPT-OSS with function calling
"""

import subprocess
import json
from pathlib import Path
from openai import OpenAI


def test_file_read_tool(user_message: str, filename: str = None):
    """Test the file read tool functionality"""
    print(f"🔍 Testing: {user_message}")
    
    # Initialize OpenAI client pointing to Ollama
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    
    # Define the file_read tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "file_read",
                "description": "Read contents of a file with syntax highlighting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name or path of file to read"
                        }
                    },
                    "required": ["filename"]
                }
            }
        }
    ]
    
    try:
        # Call GPT-OSS with tools
        print("📡 Calling GPT-OSS...")
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=[
                {"role": "system", "content": "You are GPT OSS, an AI assistant. Use the file_read function to read files when requested."},
                {"role": "user", "content": user_message}
            ],
            tools=tools
        )
        
        message = response.choices[0].message
        print(f"💬 Response: {message.content}")
        
        # Check for tool calls
        if message.tool_calls:
            print(f"🔧 Tool calls found: {len(message.tool_calls)}")
            
            for tool_call in message.tool_calls:
                print(f"🔧 Tool: {tool_call.function.name}")
                print(f"🔧 Args: {tool_call.function.arguments}")
                
                if tool_call.function.name == "file_read":
                    args = json.loads(tool_call.function.arguments)
                    filename = args.get("filename")
                    print(f"📄 Reading file: {filename}")
                    
                    # Execute the read tool
                    result = execute_read_tool(filename)
                    print(f"📄 Result:\n{result}")
                    
                    return result
        else:
            print("❌ No tool calls found")
            return message.content
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return str(e)


def execute_read_tool(filename: str) -> str:
    """Execute the ./read tool"""
    try:
        tools_dir = Path(__file__).parent
        cmd = ["./read", filename]
        
        print(f"🏃 Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=tools_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return f"✅ Success:\n```\n{result.stdout}\n```"
        else:
            return f"❌ Error reading {filename}:\n```\n{result.stderr}\n```"
            
    except Exception as e:
        return f"❌ Failed to execute read tool: {str(e)}"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Read the config.yaml file",
        "Show me config.yaml",  
        "What's in requirements.txt?",
        "Read thinking.md"
    ]
    
    print("🚀 Starting file read tool tests...")
    
    for test in test_cases:
        print("\n" + "="*50)
        result = test_file_read_tool(test)
        print(f"Final result: {result[:100]}...")
        print("="*50)