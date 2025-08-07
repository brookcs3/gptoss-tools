#!/usr/bin/env python3
"""
GPT OSS TUI - Complete Claude Code-style Interface
Full AI chat integration with tool calling capabilities
"""

import subprocess
import os
import json
import requests
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Harmony format imports
from openai_harmony import (
    SystemContent, 
    Message as HarmonyMessage, 
    Conversation, 
    Role as HarmonyRole, 
    TextContent,
    Author,
    load_harmony_encoding, 
    HarmonyEncodingName
)

# Import our GPT-OSS tools
from gptoss_tools import GPTOSS_TOOLS, get_tool_configs

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, ListView, ListItem,
    Label, Placeholder, DirectoryTree, Log, Select, TextArea,
    Markdown, ProgressBar, Switch
)
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message as TextualMessage
from textual.worker import Worker

# Import our custom panels
from thinking_panel import ThinkingPanel


class ChatMessage(Container):
    """Individual chat message widget"""
    
    def __init__(self, role: str, content: str, timestamp: str = None):
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
    
    def compose(self) -> ComposeResult:
        role_icon = "🤖" if self.role == "assistant" else "👤"
        role_style = "dim" if self.role == "assistant" else "bold"
        
        with Horizontal():
            yield Static(f"{role_icon} {self.role.title()}", classes=f"role {role_style}")
            yield Static(self.timestamp, classes="timestamp dim")
        
        # Use Static for all messages to avoid Markdown crashes with emojis/special chars
        yield Static(self.content, classes="message-content")


class ChatPanel(Container):
    """Main chat interface panel with Harmony integration"""
    
    messages = reactive([])
    
    def __init__(self):
        super().__init__()
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "gpt-oss:20b"
        self.conversation_history = []
        
        # Initialize Harmony encoding
        try:
            self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
        except Exception as e:
            print(f"Warning: Could not load Harmony encoding: {e}")
            self.encoding = None
        
        # Initialize tools
        self.tools = GPTOSS_TOOLS
    
    def compose(self) -> ComposeResult:
        yield Label("🤖 GPT OSS Chat", classes="panel-header")
        
        with ScrollableContainer(id="chat_history", classes="chat-scroll"):
            yield Static("Welcome to GPT OSS! Ask me anything or request tool operations.", 
                        classes="welcome-message")
        
        with Horizontal(classes="chat_input-area"):
            yield Input(placeholder="Ask GPT OSS anything...", id="chat_input")
            yield Button("Send", id="send_btn", variant="primary")
            yield Button("Tools", id="tools_btn", variant="default")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            self.send_message()
        elif event.button.id == "tools_btn":
            self.show_tools_help()
    
    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "chat_input":
            self.send_message()
    
    def send_message(self):
        """Send user message and get AI response"""
        chat_input = self.query_one("#chat_input", Input)
        user_message = chat_input.value.strip()
        
        if not user_message:
            return
        
        # Add user message to chat
        self.add_message("user", user_message)
        chat_input.value = ""
        
        # Get AI response
        self.get_ai_response(user_message)
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history with proper scrolling"""
        if not content.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_history = self.query_one("#chat_history", ScrollableContainer)

        # Remove welcome message if it exists
        if chat_history.children and "Welcome to GPT OSS" in str(chat_history.children[0]):
            chat_history.children[0].remove()

        # Create role header (like ThinkingPanel's timestamp approach)
        role_icon = "🤖" if role == "assistant" else "👤"
        role_style = "chat-role-dim" if role == "assistant" else "chat-role-bold"
        
        role_widget = Static(f"{role_icon} {role.title()} {timestamp}")
        role_widget.add_class(role_style)
        chat_history.mount(role_widget)

        # Create content widget (like ThinkingPanel's content approach)
        content_widget = Static(content)
        content_widget.add_class("chat-content")
        chat_history.mount(content_widget)

        # Auto-scroll to bottom (same as ThinkingPanel)
        chat_history.scroll_end()
    
    def get_ai_response(self, user_message: str):
        """Get response from GPT OSS model using Harmony format"""
        try:
            # Show typing indicator
            self.add_message("assistant", "🤔 Thinking...")
            
            # Create Harmony conversation
            if self.encoding:
                response = self._call_ollama_harmony(user_message)
            else:
                # Fallback to simple API if Harmony fails
                response = self._call_ollama_simple(user_message)
            
            # Remove typing indicator 
            chat_history = self.query_one("#chat_history", ScrollableContainer)
            if chat_history.children:
                chat_history.children[-1].remove()
            
            self.add_message("assistant", response)
            
        except Exception as e:
            # Remove typing indicator
            chat_history = self.query_one("#chat_history", ScrollableContainer)
            if chat_history.children:
                chat_history.children[-1].remove()
            
            error_msg = f"❌ Error: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"
            self.add_message("assistant", error_msg)
    
    def _call_ollama_harmony(self, user_message: str) -> str:
        """Call Ollama using Harmony format with tool support"""
        try:
            # Create system message with tools
            system_content = SystemContent.new().with_conversation_start_date(
                datetime.now().strftime("%Y-%m-%d")
            ).with_tools([tool_config for tool_config in get_tool_configs()])
            
            system_message = HarmonyMessage.from_role_and_content(
                HarmonyRole.SYSTEM, system_content
            )
            
            # Add conversation history 
            messages = [system_message] + self.conversation_history
            
            # Add current user message
            user_msg = HarmonyMessage.from_role_and_content(
                HarmonyRole.USER, TextContent(text=user_message)
            )
            messages.append(user_msg)
            self.conversation_history.append(user_msg)
            
            # Create conversation
            conversation = Conversation.from_messages(messages)
            
            # Convert to tokens for Ollama
            token_ids = self.encoding.render_conversation_for_completion(
                conversation, HarmonyRole.ASSISTANT
            )
            
            # Call Ollama with chat API
            ollama_messages = []
            for msg in messages:
                if msg.author.role == HarmonyRole.SYSTEM:
                    ollama_messages.append({"role": "system", "content": str(msg.content)})
                elif msg.author.role == HarmonyRole.USER:
                    ollama_messages.append({"role": "user", "content": msg.content.text})
                elif msg.author.role == HarmonyRole.ASSISTANT:
                    ollama_messages.append({"role": "assistant", "content": str(msg.content)})
            
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {"temperature": 1.0}
                },
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_response = result.get("message", {}).get("content", "No response")
            
            # Parse response for tool calls
            self._handle_harmony_response(assistant_response)
            
            return assistant_response
            
        except Exception as e:
            print(f"Harmony API failed: {e}")
            return self._call_ollama_simple(user_message)
    
    def _call_ollama_simple(self, user_message: str) -> str:
        """Fallback simple Ollama API call"""
        system_prompt = """You are GPT OSS, an AI development assistant with access to file tools.
        
Available operations:
- To find files: Use "file_operations find <pattern>" 
- To read files: Use "file_operations read <filename>"
- To search text: Use "file_operations grep <query>"
- To semantic search: Use "file_operations search <query>"
- To analyze project: Use "file_operations analyze codebase"
- To create files: Use "file_writer create <filename>"

When users ask for file operations, use the exact format above."""
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            },
            timeout=90
        )
        response.raise_for_status()
        
        result = response.json()
        assistant_response = result.get("message", {}).get("content", "No response")
        
        # Handle simple tool suggestions
        self._handle_simple_tool_suggestions(assistant_response)
        
        return assistant_response
    
    def _handle_harmony_response(self, response: str):
        """Handle Harmony-formatted response with potential tool calls"""
        # This would parse proper Harmony tool calls
        # For now, fall back to simple parsing
        self._handle_simple_tool_suggestions(response)
    
    def _handle_simple_tool_suggestions(self, response: str):
        """Handle simple tool suggestions in AI response"""
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for tool operation patterns
            if "file_operations" in line or "file_writer" in line:
                # Extract tool command
                if line.startswith('"') and line.endswith('"'):
                    command = line[1:-1]  # Remove quotes
                elif '"' in line:
                    # Extract quoted command
                    start = line.find('"') + 1
                    end = line.rfind('"')
                    if start < end:
                        command = line[start:end]
                    else:
                        continue
                else:
                    command = line
                
                # Execute the tool command
                if command.startswith(("file_operations", "file_writer")):
                    self._execute_harmony_tool(command)
    
    def _execute_harmony_tool(self, command: str):
        """Execute a harmony tool command"""
        try:
            parts = command.split(" ", 1)
            if len(parts) < 2:
                return
                
            tool_name = parts[0]
            tool_args = parts[1]
            
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                
                # Create a mock Harmony message for the tool
                tool_message = HarmonyMessage(
                    author=Author(role=HarmonyRole.USER, name="user"),
                    content=TextContent(text=tool_args)
                )
                
                # Execute tool (simplified sync version)
                try:
                    # This is a simplified sync execution
                    # In a real implementation, this should be async
                    result = asyncio.run(self._run_tool_async(tool, tool_message))
                    if result:
                        self.add_message("assistant", result)
                except Exception as tool_error:
                    self.add_message("assistant", f"❌ Tool error: {str(tool_error)}")
                    
        except Exception as e:
            self.add_message("assistant", f"❌ Tool execution failed: {str(e)}")
    
    async def _run_tool_async(self, tool, message):
        """Run tool asynchronously and return result"""
        results = []
        async for response_msg in tool.process(message):
            if response_msg.content:
                results.append(str(response_msg.content))
        return "\n".join(results) if results else "Tool executed successfully"
    
    def show_tools_help(self):
        """Show available tools with Harmony format"""
        tools_help = """## 🛠️ Available Tools

**File Operations Tool (`file_operations`):**
- `find *.py` - Find Python files
- `read config.yaml` - View file contents with syntax highlighting
- `grep function --recursive` - Search for text in files
- `search authentication` - Semantic search through codebase
- `analyze codebase` - Get project structure overview

**File Writer Tool (`file_writer`):**
- `create main.py --template=python` - Create new files with templates
- `edit README.md --operation=append` - Edit existing files
- `backup --all` - Create file backups
- `templates` - List available file templates

**Natural Language Examples:**
- "Find all Python files in this project" 
- "Show me the configuration file"
- "Search for authentication code"
- "Create a new JavaScript file"
- "Analyze the project structure"

💡 Just ask naturally - I'll automatically use the right tools!"""
        
        self.add_message("assistant", tools_help)


class FileExplorer(Container):
    """Enhanced file explorer with AI integration"""
    
    current_files = reactive([])
    
    def compose(self) -> ComposeResult:
        yield Label("📁 File Explorer", classes="panel-header")
        
        with Horizontal(classes="explorer-controls"):
            yield Input(placeholder="*.py", id="file_pattern", value="*.py")
            yield Button("Find", id="find_files_btn", variant="success")
            yield Button("Refresh", id="refresh_btn", variant="default")
        
        with ScrollableContainer(id="file_list"):
            yield Static("Use 'Find' to discover files...", classes="placeholder-text")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "find_files_btn":
            self.find_files()
        elif event.button.id == "refresh_btn":
            self.find_files()
        # Handle file selection
        elif hasattr(event.button, 'file_path'):
            self.open_file(event.button.file_path)
    
    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "file_pattern":
            self.find_files()
    
    def find_files(self):
        """Find files using glop tool"""
        pattern_input = self.query_one("#file_pattern", Input)
        pattern = pattern_input.value.strip() or "*.py"
        
        try:
            tools_dir = Path(__file__).parent
            result = subprocess.run(
                ["./glop", pattern, "--recursive"], 
                cwd=tools_dir,
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                files = [line for line in result.stdout.split('\n') 
                        if line.strip() and not line.startswith('Found')]
                self._update_file_list(files[:20])  # Limit to 20
            else:
                self._update_file_list([f"Error: {result.stderr}"])
                
        except Exception as e:
            self._update_file_list([f"Error: {str(e)}"])
    
    def _update_file_list(self, files: List[str]):
        """Update the file list display"""
        file_list = self.query_one("#file_list", ScrollableContainer)
        file_list.remove_children()
        
        if not files:
            file_list.mount(Static("No files found", classes="placeholder-text"))
            return
        
        for file_path in files:
            if file_path.strip():
                file_name = Path(file_path).name
                file_item = Button(
                    f"📄 {file_name}", 
                    id=f"file_{hash(file_path)}", 
                    classes="file-item"
                )
                file_item.file_path = file_path  # Store full path
                file_list.mount(file_item)

    def open_file(self, file_path: str):
        """Open file in code viewer"""
        app = self.app
        code_viewer = app.query_one("#code_viewer", CodeViewer)
        code_viewer.load_file(file_path)


class CodeViewer(Container):
    """Code viewer with syntax highlighting"""
    
    current_file = reactive("")
    
    def compose(self) -> ComposeResult:
        yield Label("📄 Code Viewer", classes="panel-header")
        
        with Horizontal(classes="viewer-controls"):
            yield Static("No file selected", id="file_info", classes="file-info")
            yield Button("AI Analyze", id="analyze_btn", variant="primary")
        
        yield TextArea("", language="python", theme="monokai", id="code_content", read_only=True)
    
    def load_file(self, file_path: str):
        """Load file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update file info
            file_info = self.query_one("#file_info", Static)
            file_name = Path(file_path).name
            file_info.update(f"📄 {file_name}")
            
            # Update content
            code_content = self.query_one("#code_content", TextArea)
            code_content.text = content
            
            # Set language based on extension
            ext = Path(file_path).suffix.lower()
            lang_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.md': 'markdown', '.yaml': 'yaml', '.yml': 'yaml',
                '.json': 'json', '.sh': 'bash', '.css': 'css'
            }
            code_content.language = lang_map.get(ext, 'text')
            
            self.current_file = file_path
            
        except Exception as e:
            file_info = self.query_one("#file_info", Static)
            file_info.update(f"❌ Error: {str(e)}")
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "analyze_btn" and self.current_file:
            self.analyze_with_ai()
    
    def analyze_with_ai(self):
        """Send current file to AI for analysis"""
        if not self.current_file:
            return
        
        chat_panel = self.app.query_one(ChatPanel)
        file_name = Path(self.current_file).name
        
        # Add analysis request to chat
        analysis_request = f"Please analyze this file: {file_name}"
        chat_panel.add_message("user", analysis_request)
        
        # Prepare file content for AI
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ai_prompt = f"Analyze this {file_name} file:\n\n```\n{content[:2000]}\n```\n\nProvide insights about its purpose, structure, and any suggestions for improvement."
            chat_panel.get_ai_response(ai_prompt)
            
        except Exception as e:
            chat_panel.add_message("assistant", f"❌ Error reading file: {str(e)}")


class ToolsPanel(Container):
    """Tools and commands panel"""
    
    def compose(self) -> ComposeResult:
        yield Label("⚙️ Tools & Commands", classes="panel-header")
        
        with Vertical(classes="tools-grid"):
            # Quick action buttons
            yield Button("🔍 Find Python Files", id="find_py", variant="success")
            yield Button("📊 Analyze Codebase", id="analyze_codebase", variant="primary")
            yield Button("🔎 Search Content", id="search_content", variant="default")
            yield Button("📋 Project Status", id="project_status", variant="warning")
        
        yield Label("Recent Commands:", classes="section-header")
        yield Log(id="command_log", max_lines=8)
    
    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        chat_panel = self.app.query_one(ChatPanel)
        
        if button_id == "find_py":
            chat_panel.add_message("user", "Find all Python files in this project")
            chat_panel.get_ai_response("Find all Python files in this project using the glop tool")
            
        elif button_id == "analyze_codebase":
            chat_panel.add_message("user", "Analyze the structure of this codebase")
            chat_panel.get_ai_response("Analyze this codebase structure using readymyfiles and provide insights")
            
        elif button_id == "search_content":
            chat_panel.add_message("user", "What can I search for in this project?")
            chat_panel.get_ai_response("Help me understand what I can search for in this codebase")
            
        elif button_id == "project_status":
            chat_panel.add_message("user", "Show me the status of GPT OSS tools")
            chat_panel.get_ai_response("Check the status of all GPT OSS tools and Ollama")
    
    def log_command(self, command: str, result: str):
        """Log a command execution"""
        log = self.query_one("#command_log", Log)
        log.write_line(f"$ {command}")
        if result:
            log.write_line(f"✅ {result[:100]}")


class GPTOSSApp(App):
    """Main GPT OSS Application - Claude Code style"""
    
    TITLE = "GPT OSS - AI Development Environment"
    SUB_TITLE = "Powered by Ollama + GPT OSS 20B"
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+c", "copy_thinking", "Copy Thinking", priority=True),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+t", "focus_chat", "Focus Chat"),
        Binding("ctrl+f", "focus_files", "Focus Files"),
        Binding("f1", "help", "Help"),
    ]
    
    def smart_copy_to_clipboard(self, text: str) -> None:
        """Smart clipboard with OSC 52 and pyperclip fallback"""
        if not text.strip():
            return
            
        # Check terminal capability
        term_program = os.environ.get("TERM_PROGRAM", "")
        
        if term_program == "Apple_Terminal":
            # macOS Terminal doesn't support OSC 52
            self._copy_with_pyperclip(text)
        else:
            try:
                # Try OSC 52 first (works over SSH)
                super().copy_to_clipboard(text)
                self.notify("📋 Copied via terminal!", severity="information")
            except:
                # Fall back to pyperclip
                self._copy_with_pyperclip(text)

    def _copy_with_pyperclip(self, text: str) -> None:
        """Fallback clipboard using pyperclip"""
        try:
            import pyperclip
            pyperclip.copy(text)
            self.notify("📋 Copied to clipboard!", severity="information")
        except ImportError:
            self.notify("❌ Install pyperclip: pip install pyperclip", severity="error")
        except Exception as e:
            self.notify(f"❌ Copy failed: {e}", severity="error")

    def action_copy_thinking(self) -> None:
        """Copy all thinking text to clipboard"""
        thinking_panel = self.query_one("#thinking_panel", ThinkingPanel)
        thinking_text = thinking_panel.get_all_thinking_text()
        if thinking_text:
            self.smart_copy_to_clipboard(thinking_text)
        else:
            self.notify("💭 No thinking text to copy", severity="warning")
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Main 1x2 grid layout - Chat + Thinking Panel only  
        with Grid(id="main_grid"):
            chat_panel = ChatPanel()
            chat_panel.id = "chat_panel"
            yield chat_panel

            thinking_panel = ThinkingPanel()
            thinking_panel.id = "thinking_panel"
            yield thinking_panel
        
        yield Footer()
    
    def on_mount(self):
        """Initialize the app"""
        # Welcome message
        chat_panel = self.query_one(ChatPanel)
        welcome_msg = """🚀 **Welcome to GPT OSS!**

I'm your AI development assistant. I can help you:
- 🔍 **Find and analyze files** in your project
- 📝 **Read and understand code** with syntax highlighting  
- 🔎 **Search through codebases** semantically
- ⚙️ **Execute development tools** automatically
- 📊 **Analyze project structure** and dependencies

**Quick Start:**
- Type naturally: "Find all Python files"
- Use the Tools panel for quick actions
- Click files in the explorer to view them
- Ask me to analyze any code you're viewing

**Try asking:**
- "What Python files are in this project?"
- "Show me the config file"
- "Analyze the project structure"
- "Search for authentication code"

What would you like to explore first?"""
        
        chat_panel.add_message("assistant", welcome_msg)
    
    def action_focus_chat(self):
        """Focus the chat input"""
        chat_input = self.query_one("#chat_input", Input)
        chat_input.focus()
    
    def action_focus_files(self):
        """Focus the file pattern input"""
        file_pattern = self.query_one("#file_pattern", Input)
        file_pattern.focus()
    
    def action_refresh(self):
        """Refresh all panels"""
        thinking_panel = self.query_one(ThinkingPanel)
        thinking_panel.clear_thinking()
    
    def action_help(self):
        """Show help"""
        chat_panel = self.query_one(ChatPanel)
        chat_panel.show_tools_help()


# Enhanced CSS for Claude Code-like styling
CSS = """
/* Main Grid Layout */
Grid#main_grid {
    grid-size: 2 1;
    grid-gutter: 1;
    height: 100%;
}

/* Panel positioning */
#chat_panel {
    column-span: 1;
    row-span: 2;
    background: $surface;
    border: solid $primary;
}

#thinking_panel {
    column-span: 1;
    row-span: 2;  
    background: $surface;
    border: solid $secondary;
}

/* Panel headers */
.panel-header {
    text-style: bold;
    background: $boost;
    padding: 0 1;
    margin-bottom: 0;
}

/* Chat styling */
.role {
    width: 12;
    text-style: bold;
}

.timestamp {
    width: 8;
    text-align: right;
}

.message-content {
    margin: 0 0 1 0;
}

.welcome-message {
    color: $text-muted;
    margin: 1;
    text-style: italic;
}

.chat-input-area {
    height: 3;
    margin: 0 0;
}

/* File explorer styling */
.explorer-controls {
    height: 3;
    margin: 0 0 1 0;
}

.file-item {
    width: 100%;
    text-align: left;
    margin: 0 0 1 0;
}

.placeholder-text {
    color: $text-muted;
    text-style: italic;
    margin: 1;
}

/* Code viewer styling */
.viewer-controls {
    height: 3;
    margin: 0 0 1 0;
}

.file-info {
    color: $text-muted;
}

#code_content {
    border: solid $accent;
}

/* Tools panel styling */
.tools-grid {
    margin: 0 0 1 0;
}

.tools-grid Button {
    width: 100%;
    margin: 0 0 1 0;
    text-align: left;
}

.section-header {
    text-style: bold;
    margin: 1 0;
    color: $text-muted;
}

#command_log {
    border: solid $accent;
    height: 8;
}

/* Input and button styling */
Input {
    margin: 0 1 0 0;
}

Button {
    margin: 0;
}

/* Scrollable containers */
ScrollableContainer {
    scrollbar-gutter: stable;
}

.chat-scroll {
    height: 1fr;
}

.thinking-scroll {
    height: 1fr;
}

#chat_history {
    height: 90%;
    border: solid $accent;
    margin: 0 0 1 0;
    scrollbar-gutter: stable;
}

#file_list {
    height: 1fr;
    border: solid $accent;
}

/* Chat Panel Styles - matching ThinkingPanel approach */
.chat-role-dim {
    color: $text-disabled;
    text-style: bold dim;
    margin: 1 0 0 0;
}

.chat-role-bold {
    color: $text-disabled;
    text-style: bold;
    margin: 1 0 0 0;
}

.chat-content {
    color: $text;
    margin: 0 0 0 1;
    padding: 0 1;
    background: $panel;
    border-left: solid $accent;
}

/* Thinking Panel Styles */
.thinking-controls {
    height: 0;
    margin: 0 0 0 0;
}

.thinking-info {
    color: $text-muted;
    text-style: italic;
}

.small-btn {
    min-width: 8;
}

#thinking_content {
    height: 1fr;
    border: solid $accent;
    scrollbar-gutter: stable;
}

.thinking-placeholder {
    color: $text-muted;
    text-style: italic;
    text-align: center;
    margin: 2;
}

.thinking-timestamp {
    color: $text-disabled;
    text-style: bold;
    margin: 1 0 0 0;
}

.thinking-content {
    color: $text;
    margin: 0 0 1 1;
    padding: 0 1;
    background: $panel;
    border-left: solid $accent;
}

.thinking-entry {
    margin: 0 0 1 0;
}
"""


def main():
    """Run the GPT OSS Application"""
    app = GPTOSSApp()
    app.CSS = CSS
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Thanks for using GPT OSS!")


if __name__ == "__main__":
    main()
