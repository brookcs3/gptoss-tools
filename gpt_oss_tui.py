#!/usr/bin/env python3
"""
GPT OSS TUI - Complete Claude Code-style Interface
Full AI chat integration with tool calling capabilities
"""

import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

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
from textual.message import Message
from textual.worker import Worker

# Import our custom ThinkingPanel
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
        
        if self.role == "assistant":
            # Render AI responses as markdown for better formatting
            yield Markdown(self.content, classes="message-content")
        else:
            yield Static(self.content, classes="message-content")


class ChatPanel(Container):
    """Main chat interface panel"""
    
    messages = reactive([])
    
    def __init__(self):
        super().__init__()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "gpt-oss:20b"
    
    def compose(self) -> ComposeResult:
        yield Label("🤖 GPT OSS Chat", classes="panel-header")
        
        with ScrollableContainer(id="chat_history"):
            yield Static("Welcome to GPT OSS! Ask me anything or request tool operations.", 
                        classes="welcome-message")
        
        with Horizontal(classes="chat-input-area"):
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
        """Add a message to the chat history"""
        chat_history = self.query_one("#chat_history", ScrollableContainer)
        message = ChatMessage(role, content)
        chat_history.mount(message)
        chat_history.scroll_end()
    
    def get_ai_response(self, user_message: str):
        """Get response from GPT OSS model"""
        try:
            # Show typing indicator
            self.add_message("assistant", "🤔 Thinking...")
            
            # Prepare the prompt with system context
            system_prompt = """You are GPT OSS, an AI assistant integrated into a powerful development toolkit. You can help with:

1. **File Operations**: Finding, reading, and analyzing files
2. **Code Search**: Searching through codebases and finding patterns  
3. **Project Analysis**: Understanding project structure and dependencies
4. **Tool Execution**: Running development tools and commands

Available tools in this environment:
- `glop <pattern>` - Find files by pattern (e.g., "*.py", "*.js")
- `grep <query>` - Search file contents for text patterns
- `search <query>` - Semantic search through indexed files
- `read <file>` - Display file contents with syntax highlighting
- `readymyfiles` - Prepare files for AI analysis
- `filewrite` - Create and edit files

When users ask you to perform actions, suggest specific tool commands or execute them if requested. Be helpful, practical, and focus on developer productivity.

User message: """
            
            # Call Ollama API
            response = self._call_ollama(system_prompt + user_message)
            
            # Remove typing indicator and add real response
            chat_history = self.query_one("#chat_history", ScrollableContainer)
            if chat_history.children:
                chat_history.children[-1].remove()
            
            self.add_message("assistant", response)
            
            # Check if response contains tool suggestions
            self._handle_tool_suggestions(response)
            
        except Exception as e:
            # Remove typing indicator
            chat_history = self.query_one("#chat_history", ScrollableContainer)
            if chat_history.children:
                chat_history.children[-1].remove()
            
            error_msg = f"❌ Error: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"
            self.add_message("assistant", error_msg)
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API synchronously"""
        import requests
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
        
        response = requests.post(self.ollama_url, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract thinking and send to ThinkingPanel
        thinking = result.get("thinking", "")
        if thinking.strip():
            thinking_panel = self.app.query_one("#thinking_panel", ThinkingPanel)
            thinking_panel.add_thinking(thinking)
        
        return result.get("response", "No response generated")
    
    def _handle_tool_suggestions(self, response: str):
        """Execute tool commands suggested by AI"""
        # Look for tool commands in response (simple pattern matching)
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('`') and line.endswith('`'):
                # Extract command from code block
                command = line[1:-1]
                if any(tool in command for tool in ['glop', 'grep', 'search', 'read']):
                    # Auto-execute the suggested command
                    self._execute_tool_command(command)
    
    def _execute_tool_command(self, command: str):
        """Execute a tool command and show results"""
        try:
            tools_dir = Path(__file__).parent
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=tools_dir,
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.stdout:
                output = f"📋 Command: `{command}`\n\n```\n{result.stdout}\n```"
                self.add_message("assistant", output)
            
            if result.stderr:
                error = f"⚠️ Command error: `{command}`\n\n```\n{result.stderr}\n```"
                self.add_message("assistant", error)
                
        except Exception as e:
            error = f"❌ Failed to execute: `{command}`\n\nError: {str(e)}"
            self.add_message("assistant", error)
    
    def show_tools_help(self):
        """Show available tools"""
        tools_help = """## Available Tools

**File Operations:**
- `glop "*.py"` - Find Python files
- `read config.yaml` - View file contents
- `grep "function"` - Search for text in files

**Search & Analysis:**
- `search "authentication"` - Semantic search
- `readymyfiles analyze-codebase` - Project analysis

**Examples:**
- "Find all Python files in this project"
- "Search for authentication code"
- "Show me the config file"
- "Analyze this codebase structure"

Just ask naturally - I'll suggest the right tools!"""
        
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
        
        # Main 2x2 grid layout
        with Grid(id="main_grid"):
            chat_panel = ChatPanel()
            chat_panel.id = "chat_panel"
            yield chat_panel
            
            thinking_panel = ThinkingPanel()
            thinking_panel.id = "thinking_panel"
            yield thinking_panel

            code_viewer = CodeViewer()
            code_viewer.id = "code_viewer"
            yield code_viewer
            
            tools_panel = ToolsPanel()
            tools_panel.id = "tools_panel"
            yield tools_panel
        
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
    grid-size: 2 2;
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
    row-span: 1;  
    background: $surface;
    border: solid $secondary;
}

#code_viewer {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $success;
}

#tools_panel {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $warning;
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
    margin: 1 0;
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

#chat_history {
    height: 1fr;
    border: solid $accent;
    margin: 0 0 1 0;
}

#file_list {
    height: 1fr;
    border: solid $accent;
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
