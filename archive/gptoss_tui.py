#!/usr/bin/env python3
"""
GPT OSS TUI - Modern Terminal Interface
A rich, interactive terminal UI for GPT OSS tools with Yoga-like layouts
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, Input, TextArea, Tree, 
    DataTable, Log, TabbedContent, TabPane, DirectoryTree,
    ProgressBar, Switch, Select, Label
)
from textual.reactive import reactive
from textual.message import Message
from textual.screen import Screen
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class FileExplorer(Container):
    """File explorer with tree view"""
    
    def compose(self) -> ComposeResult:
        yield Label("📁 File Explorer")
        yield DirectoryTree(".", id="file_tree")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection"""
        self.app.call_from_thread(self.app.show_file_content, str(event.path))


class SearchPanel(Container):
    """Search interface with patterns and results"""
    
    def compose(self) -> ComposeResult:
        yield Label("🔍 Search & Patterns")
        with Horizontal():
            yield Input(placeholder="Search pattern...", id="search_input")
            yield Button("Search", id="search_btn", variant="primary")
        
        with Horizontal():
            yield Button("*.py", id="py_filter", variant="default")
            yield Button("*.js", id="js_filter", variant="default") 
            yield Button("*.md", id="md_filter", variant="default")
            yield Button("class|def", id="code_pattern", variant="default")
        
        yield ScrollableContainer(id="search_results")


class CodeViewer(Container):
    """Code viewer with syntax highlighting"""
    
    current_file = reactive("")
    
    def compose(self) -> ComposeResult:
        yield Label("📄 Code Viewer")
        yield TextArea("", language="python", theme="monokai", id="code_area", read_only=True)
    
    def watch_current_file(self, file_path: str) -> None:
        """Update code viewer when file changes"""
        if file_path and Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read()
            code_area = self.query_one("#code_area", TextArea)
            code_area.text = content
            
            # Set language based on extension
            ext = Path(file_path).suffix
            lang_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.md': 'markdown', '.yaml': 'yaml', '.yml': 'yaml',
                '.json': 'json', '.sh': 'bash'
            }
            code_area.language = lang_map.get(ext, 'text')


class CommandInterface(Container):
    """Command runner with history and output"""
    
    def compose(self) -> ComposeResult:
        yield Label("💻 GPT OSS Commands")
        with Horizontal():
            yield Input(placeholder="Enter command...", id="cmd_input")
            yield Button("Run", id="run_btn", variant="success")
        
        with Horizontal():
            yield Button("glop *.py", id="glop_cmd", variant="default")
            yield Button("search index", id="index_cmd", variant="default") 
            yield Button("grep 'def'", id="grep_cmd", variant="default")
            yield Button("readymyfiles", id="ready_cmd", variant="default")
        
        yield Log(id="command_output", auto_scroll=True)


class StatusBar(Container):
    """Status information and stats"""
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("🤖 GPT OSS Tools", id="status_title")
            yield Static("Ready", id="status_text") 
            yield Static("Files: 0", id="file_count")
            yield Static("Ollama: ✅", id="ollama_status")


class MainScreen(Screen):
    """Main application screen with panels"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with TabbedContent():
            with TabPane("Explorer", id="explorer_tab"):
                with Horizontal():
                    with Vertical(classes="left_panel"):
                        yield FileExplorer(id="file_explorer")
                        yield SearchPanel(id="search_panel")
                    
                    with Vertical(classes="right_panel"):
                        yield CodeViewer(id="code_viewer")
                        yield CommandInterface(id="command_interface")
            
            with TabPane("Analysis", id="analysis_tab"):
                yield Static("📊 Codebase Analysis Coming Soon...")
            
            with TabPane("AI Chat", id="chat_tab"):
                yield Static("🤖 GPT OSS Chat Interface Coming Soon...")
        
        yield StatusBar(id="status_bar")
        yield Footer()


class GPTOSSTUIApp(App):
    """Main GPT OSS TUI Application"""
    
    CSS_PATH = None
    TITLE = "GPT OSS TUI"
    SUB_TITLE = "Modern Terminal Interface for GPT OSS Tools"
    
    def __init__(self):
        super().__init__()
        self.tools_dir = Path(__file__).parent
    
    def compose(self) -> ComposeResult:
        yield MainScreen()
    
    def on_mount(self) -> None:
        """Initialize the app"""
        self.update_status()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "search_btn":
            self.handle_search()
        elif button_id == "run_btn":
            self.handle_command()
        elif button_id in ["py_filter", "js_filter", "md_filter"]:
            self.handle_filter(button_id)
        elif button_id in ["glop_cmd", "index_cmd", "grep_cmd", "ready_cmd"]:
            self.handle_quick_command(button_id)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submissions"""
        if event.input.id == "search_input":
            self.handle_search()
        elif event.input.id == "cmd_input":
            self.handle_command()
    
    def handle_search(self) -> None:
        """Execute search command"""
        search_input = self.query_one("#search_input", Input)
        pattern = search_input.value
        
        if pattern:
            self.run_tool_command(f"./search '{pattern}'")
            search_input.value = ""
    
    def handle_command(self) -> None:
        """Execute custom command"""
        cmd_input = self.query_one("#cmd_input", Input)
        command = cmd_input.value
        
        if command:
            self.run_tool_command(command)
            cmd_input.value = ""
    
    def handle_filter(self, filter_id: str) -> None:
        """Handle file type filters"""
        patterns = {
            "py_filter": "*.py",
            "js_filter": "*.js", 
            "md_filter": "*.md"
        }
        pattern = patterns.get(filter_id, "")
        if pattern:
            self.run_tool_command(f"./glop '{pattern}' --recursive")
    
    def handle_quick_command(self, cmd_id: str) -> None:
        """Handle quick command buttons"""
        commands = {
            "glop_cmd": "./glop '*.py' --recursive",
            "index_cmd": "./search index",
            "grep_cmd": "./grep 'def' --include='*.py'",
            "ready_cmd": "./readymyfiles analyze-codebase --report"
        }
        command = commands.get(cmd_id, "")
        if command:
            self.run_tool_command(command)
    
    def run_tool_command(self, command: str) -> None:
        """Execute a GPT OSS tool command"""
        try:
            log = self.query_one("#command_output", Log)
            log.write_line(f"$ {command}")
            
            # Run command in tools directory
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.tools_dir,
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                log.write_line(result.stdout)
            if result.stderr:
                log.write_line(f"Error: {result.stderr}")
                
            self.update_file_count()
            
        except Exception as e:
            log = self.query_one("#command_output", Log)
            log.write_line(f"Error: {str(e)}")
    
    def show_file_content(self, file_path: str) -> None:
        """Display file content in code viewer"""
        code_viewer = self.query_one("#code_viewer", CodeViewer)
        code_viewer.current_file = file_path
    
    def update_status(self) -> None:
        """Update status information"""
        try:
            # Check Ollama status
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            ollama_status = "✅" if result.returncode == 0 else "❌"
            
            status = self.query_one("#ollama_status", Static)
            status.update(f"Ollama: {ollama_status}")
            
        except Exception:
            status = self.query_one("#ollama_status", Static) 
            status.update("Ollama: ❓")
    
    def update_file_count(self) -> None:
        """Update file count in status"""
        try:
            # Count files in current directory
            file_count = len([f for f in Path(".").rglob("*") if f.is_file()])
            status = self.query_one("#file_count", Static)
            status.update(f"Files: {file_count}")
        except Exception:
            pass


# CSS Styling for the TUI
CSS = """
Screen {
    layout: vertical;
}

.left_panel {
    width: 40%;
    height: 100%;
}

.right_panel {
    width: 60%; 
    height: 100%;
}

#file_explorer {
    height: 50%;
    border: solid $primary;
    margin: 1;
}

#search_panel {
    height: 50%;
    border: solid $secondary;
    margin: 1;
}

#code_viewer {
    height: 70%;
    border: solid $success;
    margin: 1;
}

#command_interface {
    height: 30%;
    border: solid $warning;
    margin: 1;
}

#status_bar {
    height: 3;
    background: $boost;
    border: solid $primary;
}

#command_output {
    height: 10;
    border: solid $accent;
}

Button {
    margin: 0 1;
}

Label {
    text-style: bold;
    margin-bottom: 1;
}

Input {
    margin: 0 1;
}
"""


def main():
    """Run the GPT OSS TUI application"""
    app = GPTOSSTUIApp()
    app.CSS = CSS
    app.run()


if __name__ == "__main__":
    main()
