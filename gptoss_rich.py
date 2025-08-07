#!/usr/bin/env python3
"""
Enhanced GPT OSS Tools with Rich UI
Beautiful terminal output with better formatting and layout
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text
from rich.prompt import Prompt, Confirm


console = Console()


class RichGPTOSSTools:
    """Enhanced GPT OSS tools with Rich UI"""
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with error handling"""
        config_path = self.tools_dir / "config.yaml"
        try:
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception:
            return {}
    
    def show_status(self):
        """Enhanced status display"""
        console.print()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["header"].update(
            Panel("🤖 GPT OSS Tools Dashboard", style="bold blue")
        )
        
        # Status table
        table = Table(title="System Status", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", width=15)
        table.add_column("Details", style="dim")
        
        # Check tools
        tools = ["glop", "grep", "filewrite", "read", "search", "readymyfiles"]
        for tool in tools:
            tool_path = self.tools_dir / tool
            if tool_path.exists():
                table.add_row(f"📁 {tool}", "✅ Ready", f"Executable: {tool_path}")
            else:
                table.add_row(f"📁 {tool}", "❌ Missing", f"Not found")
        
        # Check Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models = [line for line in result.stdout.split('\n') if 'gpt-oss' in line]
                if models:
                    table.add_row("🤖 Ollama", "✅ Running", f"GPT OSS models: {len(models)}")
                else:
                    table.add_row("🤖 Ollama", "⚠️ No GPT OSS", "Ollama running but no GPT OSS models")
            else:
                table.add_row("🤖 Ollama", "❌ Not Running", "Start with: ollama serve")
        except Exception as e:
            table.add_row("🤖 Ollama", "❓ Unknown", f"Error: {str(e)[:50]}")
        
        layout["body"].update(table)
        layout["footer"].update(
            Panel("Use: python3 gptoss_rich.py --help for commands", style="dim")
        )
        
        console.print(layout)
    
    def enhanced_glop(self, pattern: str, recursive: bool = False):
        """Enhanced file pattern matching with Rich output"""
        console.print(f"\n🔍 Searching for pattern: [bold cyan]{pattern}[/bold cyan]")
        
        cmd = ["./glop", pattern]
        if recursive:
            cmd.append("--recursive")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching files...", total=None)
            
            try:
                result = subprocess.run(cmd, cwd=self.tools_dir, capture_output=True, text=True)
                progress.remove_task(task)
                
                if result.returncode == 0:
                    files = [line for line in result.stdout.split('\n') if line.strip() and not line.startswith('Found')]
                    
                    if files:
                        # Create file tree
                        tree = Tree(f"📁 Found {len(files)} files")
                        for file_path in files:
                            rel_path = Path(file_path).relative_to(Path.cwd()) if Path(file_path).is_absolute() else Path(file_path)
                            tree.add(f"📄 {rel_path}")
                        
                        console.print(tree)
                        
                        # Show file details table
                        table = Table(title="File Details", show_header=True)
                        table.add_column("File", style="cyan")
                        table.add_column("Size", justify="right")
                        table.add_column("Modified", style="dim")
                        
                        for file_path in files[:10]:  # Limit to 10 files
                            try:
                                path_obj = Path(file_path)
                                if path_obj.exists():
                                    size = path_obj.stat().st_size
                                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                                    modified = path_obj.stat().st_mtime
                                    import datetime
                                    mod_str = datetime.datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M")
                                    table.add_row(str(path_obj.name), size_str, mod_str)
                            except Exception:
                                table.add_row(str(file_path), "Unknown", "Unknown")
                        
                        console.print(table)
                        
                        if len(files) > 10:
                            console.print(f"\n[dim]... and {len(files) - 10} more files[/dim]")
                    else:
                        console.print("[yellow]No files found matching pattern[/yellow]")
                else:
                    console.print(f"[red]Error: {result.stderr}[/red]")
                    
            except Exception as e:
                progress.remove_task(task)
                console.print(f"[red]Error running glop: {str(e)}[/red]")
    
    def enhanced_search(self, query: str, index_first: bool = False):
        """Enhanced search with Rich output"""
        if index_first:
            console.print("\n📊 Indexing files...")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Building search index...", total=None)
                result = subprocess.run(["./search", "index"], cwd=self.tools_dir, capture_output=True, text=True)
                progress.remove_task(task)
                
                if result.returncode == 0:
                    console.print("[green]✅ Indexing complete[/green]")
                else:
                    console.print(f"[red]Indexing failed: {result.stderr}[/red]")
                    return
        
        console.print(f"\n🔍 Searching for: [bold cyan]{query}[/bold cyan]")
        
        result = subprocess.run(["./search", query], cwd=self.tools_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse search results
            lines = result.stdout.strip().split('\n')
            if lines and "Found" in lines[0]:
                console.print(f"[green]{lines[0]}[/green]\n")
                
                # Display results in panels
                for i, line in enumerate(lines[1:], 1):
                    if line.strip():
                        console.print(Panel(line, title=f"Result {i}", border_style="blue"))
            else:
                console.print("[yellow]No results found[/yellow]")
        else:
            console.print(f"[red]Search failed: {result.stderr}[/red]")
    
    def enhanced_read(self, file_path: str, lines: int = None):
        """Enhanced file reading with syntax highlighting"""
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        console.print(f"\n📄 Reading: [bold cyan]{file_path}[/bold cyan]")
        
        try:
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine language for syntax highlighting
            ext = path_obj.suffix.lower()
            lang_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.md': 'markdown', '.yaml': 'yaml', '.yml': 'yaml',
                '.json': 'json', '.sh': 'bash', '.css': 'css',
                '.html': 'html', '.xml': 'xml', '.sql': 'sql'
            }
            language = lang_map.get(ext, 'text')
            
            # Create syntax object
            if lines:
                content_lines = content.split('\n')
                content = '\n'.join(content_lines[:lines])
                if len(content_lines) > lines:
                    content += f"\n... ({len(content_lines) - lines} more lines)"
            
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            
            # File info panel
            file_info = Table.grid(padding=1)
            file_info.add_column(style="bold blue")
            file_info.add_column()
            
            file_info.add_row("Size:", f"{len(content):,} chars")
            file_info.add_row("Lines:", f"{content.count(chr(10)) + 1:,}")
            file_info.add_row("Language:", language.title())
            
            console.print(Panel(file_info, title="File Info", border_style="green"))
            console.print(Panel(syntax, title=f"📄 {path_obj.name}", border_style="blue"))
            
        except Exception as e:
            console.print(f"[red]Error reading file: {str(e)}[/red]")
    
    def interactive_mode(self):
        """Interactive command mode"""
        console.print(Panel("🚀 GPT OSS Interactive Mode", style="bold green"))
        console.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")
        
        while True:
            try:
                command = Prompt.ask("GPT OSS", default="help")
                
                if command.lower() in ['exit', 'quit', 'q']:
                    console.print("👋 Goodbye!")
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower() == 'status':
                    self.show_status()
                elif command.startswith('glop '):
                    pattern = command[5:].strip()
                    self.enhanced_glop(pattern, recursive=True)
                elif command.startswith('search '):
                    query = command[7:].strip()
                    self.enhanced_search(query)
                elif command.startswith('read '):
                    file_path = command[5:].strip()
                    self.enhanced_read(file_path)
                elif command == 'index':
                    self.enhanced_search("", index_first=True)
                else:
                    console.print(f"[yellow]Unknown command: {command}[/yellow]")
                    
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
    
    def show_help(self):
        """Show help information"""
        help_table = Table(title="Available Commands", show_header=True)
        help_table.add_column("Command", style="cyan", width=20)
        help_table.add_column("Description", style="white")
        help_table.add_column("Example", style="dim")
        
        commands = [
            ("status", "Show system status", "status"),
            ("glop <pattern>", "Find files by pattern", "glop *.py"),
            ("search <query>", "Search file contents", "search class"),
            ("read <file>", "Display file with syntax highlighting", "read config.yaml"),
            ("index", "Build search index", "index"),
            ("help", "Show this help", "help"),
            ("exit", "Exit interactive mode", "exit")
        ]
        
        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)
        
        console.print(help_table)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GPT OSS Tools with Rich UI")
    parser.add_argument("command", nargs="?", default="interactive", 
                       help="Command to run (status, interactive, etc.)")
    parser.add_argument("--pattern", "-p", help="Pattern for glop command")
    parser.add_argument("--query", "-q", help="Query for search command")
    parser.add_argument("--file", "-f", help="File for read command")
    parser.add_argument("--recursive", "-r", action="store_true", 
                       help="Recursive search")
    parser.add_argument("--lines", "-l", type=int, help="Number of lines to read")
    
    args = parser.parse_args()
    tools = RichGPTOSSTools()
    
    if args.command == "status":
        tools.show_status()
    elif args.command == "glop":
        if args.pattern:
            tools.enhanced_glop(args.pattern, args.recursive)
        else:
            console.print("[red]Please provide a pattern with --pattern[/red]")
    elif args.command == "search":
        if args.query:
            tools.enhanced_search(args.query)
        else:
            console.print("[red]Please provide a query with --query[/red]")
    elif args.command == "read":
        if args.file:
            tools.enhanced_read(args.file, args.lines)
        else:
            console.print("[red]Please provide a file with --file[/red]")
    elif args.command == "interactive":
        tools.interactive_mode()
    else:
        tools.show_help()


if __name__ == "__main__":
    main()
