# GPT OSS Development Tools

A comprehensive toolkit for working with GPT OSS (OpenAI's open source models) running locally with Ollama.

## Tools Overview

### Core File Operations
- **`glop`** - Advanced file pattern matching and discovery
- **`grep`** - Powerful text search across files and directories  
- **`filewrite`** - File creation and editing utilities
- **`read`** - Smart file reading with syntax highlighting
- **`search`** - Content indexing and semantic search
- **`readymyfiles`** - File preparation and organization for AI workflows

### Setup & Configuration
- **`gptoss-config`** - Configure your GPT OSS environment
- **`gptoss-server`** - Manage your local Ollama server

## Quick Start

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Pull your preferred GPT OSS model:
   ```bash
   ollama pull gpt-oss:20b
   # or
   ollama pull gpt-oss:120b
   ```

3. Use the tools:
   ```bash
   ./glop "*.py" --recursive
   ./grep "function" --include="*.js"
   ./search "machine learning concepts"
   ./readymyfiles prepare-for-ai
   ```

## Installation

All tools are designed to work standalone or as part of the integrated toolkit.

```bash
cd /Users/cameronbrooks/gptoss-tools
chmod +x *.sh  # Make all shell scripts executable
```

## Integration with GPT OSS

These tools are designed to work seamlessly with your local GPT OSS setup:

- **File Discovery**: Use `glop` to find relevant files for your prompts
- **Content Search**: Use `grep` and `search` to find specific code patterns
- **File Preparation**: Use `readymyfiles` to organize files for AI analysis
- **Quick Reading**: Use `read` to examine files with context

## Configuration

Edit `config.yaml` to customize tool behavior and GPT OSS integration settings.
