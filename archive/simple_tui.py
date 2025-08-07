#!/usr/bin/env python3
"""
Simple GPT OSS TUI - Robust terminal interface
Works in limited terminal environments with proper fallbacks
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Button, Input, ListView, ListItem,
    Label, Placeholder, DirectoryTree, Log, Select
)
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding

import subprocess
import os
from pathlib import Path


class SimpleStatusWidget(Static):
    """Simple status display widget"""
    
    def on_mount(self):
        self.update_status()
    
    def update_status(self):
        """Update status information"""
        status_text = "🤖 GPT OSS Tools\n"
        status_text += "─" * 20 + "\n"
        
        # Check tools
        tools_dir = Path(__file__).parent
        tools = ["glop", "grep", "search", "read"]
        
        for tool in tools:
            if (tools_dir / tool).exists():
                status_text += f"✅ {tool}\n"
            else:
                status_text += f"❌ {tool}\n"
        
        # Check Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, timeout=3)
            if result.returncode == 0:
                status_text += "✅ Ollama\n"
            else:
                status_text += "❌ Ollama\n"
        except:
            status_text += "❓ Ollama\n"
        
        self.update(status_text)


class FileListWidget(Static):
    """Simple file list widget"""
    
    files = reactive([])
    
    def on_mount(self):
        self.find_files()
    
    def find_files(self):
        """Find Python files"""
        try:
            tools_dir = Path(__file__).parent
            result = subprocess.run(
                ["./glop", "*.py", "--recursive"], 
                cwd=tools_dir,
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                files = [line for line in result.stdout.split('\n') 
                        if line.strip() and not line.startswith('Found')]
                self.files = files[:10]  # Limit to 10 files
            else:
                self.files = ["Error finding files"]
                
        except Exception as e:
            self.files = [f"Error: {str(e)}"]
    
    def watch_files(self, files):
        """Update display when files change"""
        content = "📁 Python Files\n"
        content += "─" * 15 + "\n"
        
        for i, file_path in enumerate(files, 1):
            name = Path(file_path).name if file_path else "Unknown"
            content += f"{i:2d}. {name}\n"
        
        self.update(content)


class CommandWidget(Container):
    """Simple command input widget"""
    
    def compose(self) -> ComposeResult:
        yield Label("💻 Commands")
        yield Input(placeholder="Enter command...", id="cmd_input")
        yield Button("Run", id="run_btn")
        yield Log(id="output", max_lines=10)
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "run_btn":
            self.run_command()
    
    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "cmd_input":
            self.run_command()
    
    def run_command(self):
        """Run a command"""
        cmd_input = self.query_one("#cmd_input", Input)
        log = self.query_one("#output", Log)
        
        command = cmd_input.value.strip()
        if not command:
            return
        
        log.write_line(f"$ {command}")
        
        try:
            tools_dir = Path(__file__).parent
            
            # Simple command mapping
            if command == "status":
                log.write_line("Checking system status...")
                status_widget = self.app.query_one(SimpleStatusWidget)
                status_widget.update_status()
                log.write_line("✅ Status updated")
                
            elif command.startswith("find"):
                pattern = command.split()[-1] if len(command.split()) > 1 else "*.py"
                result = subprocess.run(
                    ["./glop", pattern], 
                    cwd=tools_dir,
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                if result.stdout:
                    log.write_line(result.stdout[:200])  # Limit output
                if result.stderr:
                    log.write_line(f"Error: {result.stderr[:100]}")
                    
            elif command.startswith("search"):
                query = command.replace("search", "").strip()
                if query:
                    result = subprocess.run(
                        ["./search", query], 
                        cwd=tools_dir,
                        capture_output=True, 
                        text=True,
                        timeout=10
                    )
                    if result.stdout:
                        log.write_line(result.stdout[:300])
                    if result.stderr:
                        log.write_line(f"Error: {result.stderr[:100]}")
                else:
                    log.write_line("Usage: search <query>")
                    
            else:
                log.write_line(f"Unknown command: {command}")
                log.write_line("Available: status, find <pattern>, search <query>")
            
        except Exception as e:
            log.write_line(f"Error: {str(e)}")
        
        cmd_input.value = ""


class SimpleTUIApp(App):
    """Simple, robust TUI app"""
    
    TITLE = "GPT OSS Simple TUI"
    CSS_PATH = None
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("h", "help", "Help"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Simple 2x2 grid layout
        with Grid(id="main_grid"):
            yield SimpleStatusWidget(id="status")
            yield FileListWidget(id="files") 
            yield CommandWidget(id="commands")
            yield Placeholder("📊 Analysis", id="analysis")
        
        yield Footer()
    
    def action_refresh(self):
        """Refresh all widgets"""
        self.query_one(SimpleStatusWidget).update_status()
        self.query_one(FileListWidget).find_files()
    
    def action_help(self):
        """Show help"""
        log = self.query_one("#output", Log)
        log.write_line("🤖 GPT OSS TUI Help")
        log.write_line("─" * 20)
        log.write_line("Commands:")
        log.write_line("  status - Show system status")
        log.write_line("  find <pattern> - Find files")
        log.write_line("  search <query> - Search content")
        log.write_line("")
        log.write_line("Keys:")
        log.write_line("  q - Quit")
        log.write_line("  r - Refresh")
        log.write_line("  h - This help")


# Simple CSS that works in limited terminals
CSS = """
Grid#main_grid {
    grid-size: 2 2;
    grid-gutter: 1;
}

#status {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $primary;
    padding: 1;
}

#files {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $secondary;
    padding: 1;
}

#commands {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $success;
    padding: 1;
}

#analysis {
    column-span: 1;
    row-span: 1;
    background: $surface;
    border: solid $warning;
    padding: 1;
}

Input {
    margin: 1 0;
}

Button {
    margin: 1 0;
}

#output {
    height: 8;
    border: solid $accent;
    margin: 1 0;
}
"""


def main():
    """Run the simple TUI"""
    app = SimpleTUIApp()
    app.CSS = CSS
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
