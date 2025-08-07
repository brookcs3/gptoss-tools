# GPT OSS TUI - Claude Code Style Interface

🤖 **Complete AI-powered development environment** with chat integration and tool calling capabilities.

## 🚀 Quick Start

```bash
# Launch the TUI (recommended)
python3 launch_tui.py

# Or launch directly
python3 gpt_oss_tui.py
```

## 🎯 Interface Layout

The TUI provides a **2x2 grid layout** similar to Claude Code:

```
┌─────────────────┬─────────────────┐
│  🤖 AI Chat     │  📁 File        │
│                 │     Explorer    │
│  - Natural      ├─────────────────┤
│    language     │  📄 Code        │
│    interface    │     Viewer      │
│  - Tool calling │                 │
│  - Auto-execute │  - Syntax       │
│                 │    highlighting │
│                 │  - AI analysis  │
├─────────────────┼─────────────────┤
│  ⚙️ Tools &     │                 │
│     Commands    │                 │
│                 │                 │
│  - Quick        │                 │
│    actions      │                 │
│  - Status       │                 │
│  - Logs         │                 │
└─────────────────┴─────────────────┘
```

## 💬 AI Chat Features

**Natural Language Interface:**
- **"Find all Python files in this project"**
- **"Show me the config file"**
- **"Analyze this codebase structure"**
- **"Search for authentication code"**

**Auto Tool Execution:**
- AI suggests tool commands
- Commands auto-execute with results
- Real-time output in chat

**Smart Context:**
- Remembers conversation history
- Understands project context
- Provides relevant suggestions

## 📁 File Explorer

**Pattern Matching:**
- Enter patterns like `*.py`, `*.js`, `src/**/*.ts`
- Click "Find" or press Enter
- Results show up to 20 files

**File Operations:**
- Click any file to open in Code Viewer
- Automatic syntax highlighting
- Integration with AI analysis

## 📄 Code Viewer

**Syntax Highlighting:**
- Supports Python, JavaScript, TypeScript, Markdown, YAML, JSON, etc.
- Monokai theme for better readability
- Line numbers and proper formatting

**AI Analysis:**
- Click "AI Analyze" button
- Sends file content to AI
- Get insights, suggestions, improvements

## ⚙️ Tools Panel

**Quick Actions:**
- 🔍 **Find Python Files** - Discover all .py files
- 📊 **Analyze Codebase** - Get project insights
- 🔎 **Search Content** - Semantic search help
- 📋 **Project Status** - Check tool status

**Command Log:**
- Shows recent command executions
- Success/error indicators
- Scrollable history

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quit application |
| `Ctrl+R` | Refresh file explorer |
| `Ctrl+T` | Focus chat input |
| `Ctrl+F` | Focus file pattern input |
| `F1` | Show help |

## 🛠️ Available Tools

The AI can execute these tools automatically:

### File Operations
```bash
glop "*.py"              # Find Python files
glop "src/**/*.js"       # Find JS files in src/
read config.yaml         # View file contents
grep "function"          # Search for text
```

### Search & Analysis
```bash
search "authentication"  # Semantic search
search index            # Build search index
readymyfiles analyze-codebase --report  # Project analysis
```

### Project Management
```bash
./gptoss status         # Check all tools
./search stats          # Search statistics
```

## 🤖 AI Integration

**System Context:**
The AI understands your development environment and can:
- Execute tools based on natural language requests
- Analyze code structure and patterns
- Provide development suggestions
- Debug issues and errors

**Example Conversations:**

**User:** "What Python files are in this project?"
**AI:** I'll find all Python files for you.
```
glop "*.py" --recursive
```
Found 5 Python files:
- gpt_oss_tui.py (main interface)
- gptoss_rich.py (rich CLI)
- simple_tui.py (basic TUI)
- ...

**User:** "Analyze the main TUI file"
**AI:** I'll analyze gpt_oss_tui.py for you...
[Provides detailed code analysis with suggestions]

## 🔧 Troubleshooting

**Ollama Connection Issues:**
```bash
# Start Ollama server
ollama serve

# Check if GPT OSS model is available
ollama list

# Pull GPT OSS model if needed
ollama pull gpt-oss:20b
```

**Tool Errors:**
```bash
# Check tool permissions
ls -la glop grep search read readymyfiles

# Make executable if needed
chmod +x glop grep search read readymyfiles
```

**Display Issues:**
```bash
# Set proper terminal environment
export TERM=xterm-256color
export COLORTERM=truecolor
```

## 📈 Advanced Usage

**Custom Prompts:**
- "Compare this file with industry best practices"
- "Find security vulnerabilities in this code"
- "Suggest performance optimizations"
- "Generate unit tests for this function"

**Workflow Integration:**
- Use with tmux for persistent sessions
- Integrate with your existing development workflow
- Combine with other GPT OSS tools

**Project Analysis:**
- "Map out the architecture of this project"
- "Find all TODO comments"
- "Identify unused code"
- "Check for missing documentation"

## 🚀 Next Steps

1. **Explore the Chat Interface** - Ask questions naturally
2. **Browse Your Files** - Use the file explorer
3. **Analyze Code** - Click files and use AI analysis
4. **Try Tool Commands** - Let AI suggest and execute tools
5. **Customize Workflows** - Build on this foundation

---

**Happy Coding with GPT OSS! 🤖✨**
