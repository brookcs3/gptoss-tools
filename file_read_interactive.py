#!/usr/bin/env python3
"""
Interactive File Read Tool - Test with follow-up questions
Uses OpenAI SDK to call GPT-OSS with function calling, then allows questions
"""

import subprocess
import json
import requests
from pathlib import Path
from openai import OpenAI


def interactive_file_chat():
    """Interactive chat with file reading capability and thinking display"""
    print("🚀 GPT-OSS Interactive File Reader with Thinking")
    print("📋 Ask me to read files, then ask questions about them!")
    print("💡 Try: 'Read config.yaml' then 'What is the default model?'")
    print("🧠 Thinking will be shown separately from responses")
    print("🚪 Type 'quit' to exit\n")
    
    # Initialize OpenAI client
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    
    # Define tools
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
        },
        {
            "type": "function", 
            "function": {
                "name": "file_search",
                "description": "Search for files using glob patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to match files (e.g. '*.py', '**/*.js')"
                        },
                        "path": {
                            "type": "string",
                            "description": "Directory to search in (optional, defaults to current)"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "grep_search",
                "description": "Search file contents using regex patterns", 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regex pattern to search for"
                        },
                        "glob": {
                            "type": "string", 
                            "description": "File glob pattern to limit search (e.g. '*.py')"
                        },
                        "path": {
                            "type": "string",
                            "description": "Directory to search in (optional)"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List files and directories",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "bash_command",
                "description": "Execute bash commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string", 
                            "description": "Path to file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to file"
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Edit existing file by replacing text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Path to file to edit"
                        },
                        "old_text": {
                            "type": "string",
                            "description": "Text to replace"
                        },
                        "new_text": {
                            "type": "string", 
                            "description": "Replacement text"
                        }
                    },
                    "required": ["filename", "old_text", "new_text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "apply_patch",
                "description": "Apply patch content to create, update or delete files locally",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patch_content": {
                            "type": "string",
                            "description": "Patch content in unified diff format"
                        },
                        "operation": {
                            "type": "string",
                            "description": "Operation type: apply, create, update, delete",
                            "default": "apply"
                        }
                    },
                    "required": ["patch_content"]
                }
            }
        }
    ]
    
    # Store conversation history
    messages = [
{"role": "system", "content": "You are GPT OSS, an AI assistant with comprehensive file operations and development tools. Available functions: file_read (read file contents), file_search (find files with glob patterns), grep_search (search file contents with regex), list_directory (list files/directories), bash_command (execute shell commands), write_file (create new files), edit_file (edit existing files), apply_patch (apply GPT-OSS patch format to create/update/delete files). Be helpful and detailed in your responses."}
    ]
    
    while True:
        # Get user input
        user_input = input("🤖 You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
            
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        try:
            print("🧠 GPT-OSS thinking...")
            
            # Call GPT-OSS with tools
            response = client.chat.completions.create(
                model="gpt-oss:20b",
                messages=messages,
                tools=tools
            )
            
            message = response.choices[0].message
            assistant_content = message.content or ""
            
            
            # Handle tool calls
            if message.tool_calls:
                print("🔧 Using tools...")
                
                # Execute tool calls
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    tool_name = tool_call.function.name
                    
                    # Execute the appropriate tool
                    tool_result = execute_tool(tool_name, args)
                    
                    # Add tool call and result to conversation
                    messages.append({
                        "role": "assistant", 
                        "content": assistant_content,
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call.id
                    })
                
                # Get final response after tool execution
                final_response = client.chat.completions.create(
                    model="gpt-oss:20b",
                    messages=messages
                )
                
                final_message = final_response.choices[0].message
                final_content = final_message.content
                
                
                print(f"🤖 GPT-OSS: {final_content}")
                
                # Add final response to history
                messages.append({"role": "assistant", "content": final_content})
                
            else:
                # No tools used, just regular response
                print(f"🤖 GPT-OSS: {assistant_content}")
                messages.append({"role": "assistant", "content": assistant_content})
            
        except Exception as e:
            print(f"❌ Error: {e}")



def execute_tool(tool_name: str, args: dict) -> str:
    """Execute the appropriate tool based on name"""
    try:
        tools_dir = Path(__file__).parent
        
        if tool_name == "file_read":
            filename = args.get("filename")
            print(f"📄 Reading: {filename}")
            cmd = ["./read", filename]
            
        elif tool_name == "file_search":
            pattern = args.get("pattern")
            path = args.get("path", ".")
            print(f"🔍 Searching files: {pattern} in {path}")
            cmd = ["find", path, "-name", pattern]
            
        elif tool_name == "grep_search":
            pattern = args.get("pattern")
            glob_pattern = args.get("glob", "*")
            path = args.get("path", ".")
            print(f"🔎 Grepping: {pattern} in {glob_pattern}")
            cmd = ["grep", "-r", "--include=" + glob_pattern, pattern, path]
            
        elif tool_name == "list_directory":
            path = args.get("path", ".")
            print(f"📂 Listing: {path}")
            cmd = ["ls", "-la", path]
            
        elif tool_name == "bash_command":
            command = args.get("command")
            print(f"⚡ Running: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=tools_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
        elif tool_name == "write_file":
            filename = args.get("filename")
            content = args.get("content")
            print(f"✏️ Writing: {filename}")
            file_path = tools_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {filename}"
            
        elif tool_name == "edit_file":
            filename = args.get("filename")
            old_text = args.get("old_text")
            new_text = args.get("new_text")
            print(f"📝 Editing: {filename}")
            file_path = tools_dir / filename
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if old_text in content:
                    updated_content = content.replace(old_text, new_text)
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    return f"Successfully updated {filename}"
                else:
                    return f"Text not found in {filename}: {old_text}"
            else:
                return f"File not found: {filename}"
                
        elif tool_name == "apply_patch":
            patch_content = args.get("patch_content", "")
            operation = args.get("operation", "apply")
            print(f"🔧 Applying patch: {operation}")
            
            # Parse patch and apply changes
            return apply_patch_content(patch_content, operation)
            
        else:
            return f"Unknown tool: {tool_name}"
        
        # Execute command-based tools
        if 'cmd' in locals():
            result = subprocess.run(
                cmd,
                cwd=tools_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
            
    except Exception as e:
        return f"Failed to execute {tool_name}: {str(e)}"


def apply_patch_content(patch_content: str, operation: str = "apply") -> str:
    """Apply GPT-OSS patch content to create, update or delete files"""
    try:
        import sys
        import os
        
        # Add gpt-oss tools to path temporarily
        gpt_oss_tools_path = str(Path(__file__).parent / "gpt-oss" / "gpt_oss" / "tools")
        if gpt_oss_tools_path not in sys.path:
            sys.path.insert(0, gpt_oss_tools_path)
        
        from apply_patch import apply_patch, DiffError
        
        # Change to our tools directory for file operations
        tools_dir = Path(__file__).parent
        old_cwd = os.getcwd()
        os.chdir(tools_dir)
        
        try:
            result = apply_patch(patch_content)
            return result
        except DiffError as e:
            return f"Patch Error: {str(e)}"
        finally:
            os.chdir(old_cwd)
            
    except ImportError:
        # Fallback to simple patch application if GPT-OSS tools not available
        return apply_simple_patch(patch_content)
    except Exception as e:
        return f"Failed to apply patch: {str(e)}"


def apply_simple_patch(patch_content: str) -> str:
    """Simple fallback patch application"""
    try:
        tools_dir = Path(__file__).parent
        lines = patch_content.strip().split('\n')
        
        current_file = None
        file_content = []
        result_messages = []
        
        for line in lines:
            if line.startswith('--- ') or line.startswith('+++ '):
                # File header
                if line.startswith('+++ '):
                    current_file = line[4:].strip()
                    if current_file.startswith('b/'):
                        current_file = current_file[2:]
                continue
                
            elif line.startswith('@@'):
                # Hunk header - ignore for simple patch application
                continue
                
            elif line.startswith('+'):
                # Addition
                file_content.append(line[1:])
                
            elif line.startswith('-'):
                # Deletion - skip this line
                continue
                
            elif line.startswith(' '):
                # Context line
                file_content.append(line[1:])
                
            else:
                # Regular line
                file_content.append(line)
        
        if current_file and file_content:
            file_path = tools_dir / current_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(file_content))
                
            result_messages.append(f"Successfully applied simple patch to {current_file}")
        
        return '\n'.join(result_messages) if result_messages else "No files processed"
        
    except Exception as e:
        return f"Failed to apply simple patch: {str(e)}"


if __name__ == "__main__":
    interactive_file_chat()