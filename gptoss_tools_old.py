#!/usr/bin/env python3
"""
GPT-OSS Tools Integration using Harmony Format
Wraps existing gptoss tools in proper Tool interface
"""

import subprocess
import json
from pathlib import Path
from typing import AsyncIterator, Any
from uuid import uuid4

from openai_harmony import (
    Author,
    Message,
    Role,
    TextContent,
)

# We'll use standard OpenAI function calling format instead of gpt_oss.tools
from abc import ABC, abstractmethod


class Tool(ABC):
    """Simple tool base class for our GPT-OSS integration"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod 
    def instruction(self) -> str:
        pass
        
    @abstractmethod
    async def _process(self, message) -> AsyncIterator:
        pass
        
    def error_message(self, error_message: str, channel: str = None):
        return f"❌ {self.name} Error: {error_message}"


class GPTOSSFileTool(Tool):
    """File operations tool that wraps glop, read, grep, search commands"""
    
    @property
    def name(self) -> str:
        return "file_operations"
    
    def instruction(self) -> str:
        return """File operations tool for finding, reading, and searching files.

Available operations:
- find: Find files by pattern (e.g., "find *.py" or "find **/*.js --recursive")  
- read: Read file contents with syntax highlighting (e.g., "read config.yaml")
- grep: Search text in files (e.g., "grep function --include=*.py")
- search: Semantic search through indexed files (e.g., "search authentication")
- analyze: Analyze project structure (e.g., "analyze codebase")

Usage format: <operation> <arguments>

Examples:
- "find *.py" - Find all Python files
- "read main.py" - Display main.py with syntax highlighting  
- "grep TODO --recursive" - Search for TODO comments in all files
- "search database connection" - Semantically search for database code
- "analyze codebase" - Get project structure overview
"""

    async def _process(self, message: Message) -> AsyncIterator[Message]:
        """Process file operation commands"""
        if not message.content or not isinstance(message.content, TextContent):
            yield self.error_message("Invalid message content")
            return
            
        command_text = message.content.text.strip()
        
        try:
            result = await self._execute_command(command_text)
            
            # Create response message
            response = Message(
                id=uuid4(),
                author=Author(role=Role.TOOL, name=self.name),
                content=TextContent(text=result),
                channel=message.channel,
            ).with_recipient("assistant")
            
            yield response
            
        except Exception as e:
            yield self.error_message(f"Tool execution failed: {str(e)}", channel=message.channel)
    
    async def _execute_command(self, command_text: str) -> str:
        """Execute the appropriate tool command"""
        parts = command_text.split()
        if not parts:
            return "❌ No command provided"
            
        operation = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        tools_dir = Path(__file__).parent
        
        # Map operations to actual tools
        if operation == "find":
            cmd = ["./glop"] + args + ["--recursive"] if "--recursive" not in args else ["./glop"] + args
        elif operation == "read":
            cmd = ["./read"] + args
        elif operation == "grep":  
            cmd = ["./grep"] + args
        elif operation == "search":
            if args:
                cmd = ["./search"] + args
            else:
                cmd = ["./search", "stats"]  # Show search status if no args
        elif operation == "analyze":
            if args and args[0] == "codebase":
                cmd = ["./readymyfiles", "analyze-codebase", "--report"]
            else:
                cmd = ["./readymyfiles"] + args
        else:
            return f"❌ Unknown operation: {operation}. Available: find, read, grep, search, analyze"
        
        # Execute the command
        try:
            result = subprocess.run(
                cmd,
                cwd=tools_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if not output:
                    return "✅ Command executed successfully (no output)"
                return f"📋 **{operation.title()} Results:**\n\n```\n{output}\n```"
            else:
                error = result.stderr.strip()
                return f"❌ **Error executing {operation}:**\n\n```\n{error}\n```"
                
        except subprocess.TimeoutExpired:
            return f"⏰ **Timeout:** {operation} command took too long (>30s)"
        except Exception as e:
            return f"❌ **Execution Error:** {str(e)}"


class GPTOSSWriteTool(Tool):
    """File writing and editing tool"""
    
    @property 
    def name(self) -> str:
        return "file_writer"
        
    def instruction(self) -> str:
        return """File writing and editing tool for creating and modifying files.

Available operations:
- create: Create new file (e.g., "create main.py --template=python")
- edit: Edit existing file (e.g., "edit config.yaml --operation=add-section")  
- backup: Create backups (e.g., "backup --all")
- templates: List available templates

Usage format: <operation> <arguments>

Examples:
- "create app.js --template=javascript" - Create new JS file with template
- "edit README.md --operation=append --value='## New Section'" - Add content
- "backup main.py" - Create backup of specific file
- "templates" - List all available file templates
"""

    async def _process(self, message: Message) -> AsyncIterator[Message]:
        """Process file writing commands"""
        if not message.content or not isinstance(message.content, TextContent):
            yield self.error_message("Invalid message content")
            return
            
        command_text = message.content.text.strip()
        
        try:
            result = await self._execute_write_command(command_text)
            
            response = Message(
                id=uuid4(),
                author=Author(role=Role.TOOL, name=self.name),
                content=TextContent(text=result),
                channel=message.channel,
            ).with_recipient("assistant")
            
            yield response
            
        except Exception as e:
            yield self.error_message(f"Write tool failed: {str(e)}", channel=message.channel)
    
    async def _execute_write_command(self, command_text: str) -> str:
        """Execute file writing command"""
        parts = command_text.split()
        if not parts:
            return "❌ No command provided"
            
        operation = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        tools_dir = Path(__file__).parent
        
        if operation in ["create", "edit", "backup", "templates"]:
            cmd = ["./filewrite", operation] + args
        else:
            return f"❌ Unknown write operation: {operation}. Available: create, edit, backup, templates"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=tools_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return f"✅ **{operation.title()} Successful:**\n\n```\n{output}\n```"
            else:
                error = result.stderr.strip()  
                return f"❌ **Write Error:**\n\n```\n{error}\n```"
                
        except subprocess.TimeoutExpired:
            return f"⏰ **Timeout:** {operation} command took too long"
        except Exception as e:
            return f"❌ **Write Error:** {str(e)}"


# For now, let's use simple dictionaries instead of ToolNamespaceConfig
# We'll use standard OpenAI function calling format
FILE_TOOL_CONFIG = {
    "type": "function",
    "function": {
        "name": "file_operations",
        "description": "Find, read, and search files in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Operation: find, read, grep, search, analyze"},
                "args": {"type": "string", "description": "Arguments for the operation"}
            },
            "required": ["operation"]
        }
    }
}

WRITE_TOOL_CONFIG = {
    "type": "function", 
    "function": {
        "name": "file_writer",
        "description": "Create and edit files with templates",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Operation: create, edit, backup, templates"},
                "filename": {"type": "string", "description": "File to create or edit"},
                "args": {"type": "string", "description": "Additional arguments"}
            },
            "required": ["operation"]
        }
    }
}

# Export tools for easy import
GPTOSS_TOOLS = {
    "file_operations": GPTOSSFileTool(),
    "file_writer": GPTOSSWriteTool(),
}

def get_tool_configs() -> list:
    """Get all tool configurations for system prompt"""
    return [FILE_TOOL_CONFIG, WRITE_TOOL_CONFIG]