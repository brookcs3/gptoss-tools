# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GPT OSS Development Tools** - A comprehensive toolkit for working with GPT OSS (OpenAI's open source models) running locally with Ollama. This repository contains multiple command-line tools and a sophisticated Terminal User Interface (TUI) for AI-powered development workflows.

## Common Development Commands

### Setup and Installation
```bash
# Initial setup
./setup.sh

# Install Python dependencies 
pip3 install -r requirements.txt

# Make tools executable (if needed)
chmod +x glop grep filewrite read search readymyfiles gptoss
```

### Testing Commands
```bash
# Test individual tools
python3 test_tools.py

# Test main TUI application
python3 gpt_oss_tui.py

# Quick tool verification
./gptoss status
```

### Development and Debugging
```bash
# Lint Python code (mentioned in requirements.txt)
flake8 *.py

# Format Python code (mentioned in requirements.txt) 
black *.py

# Run tests (mentioned in requirements.txt)
pytest
```

### Running the Application
```bash
# Main TUI interface (primary application)
python3 gpt_oss_tui.py

# Alternative interfaces
python3 gptoss_rich.py status    # Rich CLI interface
python3 quick.py files           # Quick commands
./gptoss_tmux.sh                 # tmux workspace
python3 simple_tui.py            # Basic TUI fallback
```

## Architecture Overview

### Core Tool Ecosystem
The project consists of **6 core tools** integrated with a unified interface:

- **`glop`** - Advanced file pattern matching and discovery (Python, ~300 LOC)
- **`grep`** - Powerful text search with regex support (Python, ~400 LOC) 
- **`filewrite`** - File creation/editing with templates (Python, ~450 LOC)
- **`read`** - Smart file reading with syntax highlighting (Python, ~350 LOC)
- **`search`** - Content indexing and semantic search (Python, ~550 LOC)
- **`readymyfiles`** - AI workflow file preparation (Python, ~500 LOC)

### Configuration System
**Central configuration**: `config.yaml`
- Ollama server settings (localhost:11434)
- Tool-specific parameters and limits
- File type associations and ignore patterns
- AI model configuration (default: gpt-oss:20b)

### TUI Application Architecture

**Main Application**: `gpt_oss_tui.py` (~21KB)
```
GPTOSSApp (Main TUI)
├── ChatPanel - AI chat interface with Ollama integration
├── ThinkingPanel - Real-time AI reasoning display (external module)
├── CodeViewer - Syntax-highlighted file viewer
└── ToolsPanel - Quick action buttons and status
```

**Key Innovation**: **AI Thinking Panel** - First-ever real-time AI reasoning visualization in terminal UI, showing internal model thought processes alongside responses.

### External Module Pattern
**Important**: Use external modules for complex UI components:
- `thinking_panel.py` - AI reasoning display (works perfectly)
- `chat_panel.py` - Chat interface components
- Pattern: External modules > inline widget definitions for stability

### Tool Integration Layer
- Subprocess-based tool execution with 10-second timeouts
- Auto-execution of AI-suggested commands 
- Result parsing and formatting
- Error handling with user-friendly messages

## Development Guidelines

### UI Development (Textual Framework)
- Use **external modules** for complex components (copying `thinking_panel.py` pattern)
- Prefer **separate Static widgets** over nested complex widgets
- Apply **CSS classes individually** to widgets
- Use `scrollbar-gutter: stable` for proper scrolling
- Avoid Markdown widget for user-generated content (crashes on special characters)

### Tool Development
- Follow existing tool patterns in core tools
- Integrate with `config.yaml` for settings
- Add proper error handling and timeouts
- Include help text and usage examples
- Test with `test_tools.py`

### AI Integration
- Default model: `gpt-oss:20b` (13GB)
- Server: `http://localhost:11434/v1` 
- Extract both `thinking` and `response` from API calls
- 150k token context limit (target: expand to 20B context)

## File Structure Patterns

```
gptoss-tools/
├── Core Tools (executable Python scripts)
│   ├── glop, grep, filewrite, read, search, readymyfiles
│   └── gptoss (unified interface)
├── TUI Application
│   ├── gpt_oss_tui.py (main app)
│   ├── thinking_panel.py (external module - copy this pattern)
│   ├── chat_panel.py (external module)
│   └── various other UI components
├── Configuration
│   ├── config.yaml (centralized settings)
│   └── requirements.txt (Python dependencies)
└── Development
    ├── setup.sh (installation script)
    ├── test_tools.py (testing utilities)
    └── EDIT*.md files (development session history)
```

## Dependencies and Environment

### Required Python Packages
- `PyYAML>=6.0` (configuration parsing) 
- `textual` (TUI framework)
- `requests` (Ollama API integration)

### Optional Packages
- `pygments>=2.0` (syntax highlighting)
- `pytest>=7.0` (testing) 
- `black>=22.0` (code formatting)
- `flake8>=5.0` (linting)
- `pyperclip` (clipboard functionality)

### External Dependencies  
- **Ollama** with GPT OSS models (gpt-oss:20b recommended)
- **Python 3.8+** (developed on 3.13.5)
- **Terminal** with color support (TERM=xterm-256color, COLORTERM=truecolor)

## Session Continuity Features

The project includes comprehensive session documentation in `EDIT*.md` files detailing:
- Complete development history and technical decisions
- AI thinking panel implementation breakthrough 
- UI architecture insights and debugging solutions
- Copy/paste optimization requirements
- Performance characteristics and optimization strategies

## Known Limitations and Future Enhancements

### Current Limitations
- 150k token context limit prevents full large file analysis
- Clipboard copy (Ctrl+C) functionality needs debugging
- Manual tool command execution in some cases

### Priority Enhancements
1. **Claude Code-style paste optimization** - `[Pasted text #X +N lines]` collapsible format
2. **Context limit expansion** to full 20B model capacity  
3. **Enhanced clipboard functionality** across all environments
4. **File editing integration** within TUI interface