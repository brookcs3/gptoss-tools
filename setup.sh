#!/usr/bin/env bash
# GPT OSS Tools - Setup Script

set -euo pipefail

TOOLS_DIR="/Users/cameronbrooks/gptoss-tools"
CONFIG_FILE="$TOOLS_DIR/config.yaml"

echo "🚀 Setting up GPT OSS Tools..."

# Check if we're in the right directory
if [[ ! -d "$TOOLS_DIR" ]]; then
    echo "❌ Tools directory not found: $TOOLS_DIR"
    exit 1
fi

cd "$TOOLS_DIR"

# Make all tools executable
echo "📝 Making tools executable..."
chmod +x glop grep filewrite read search readymyfiles
chmod +x setup.sh

# Check for required dependencies
echo "🔍 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for pip and install required packages
echo "📦 Installing Python dependencies..."
python3 -c "import yaml" 2>/dev/null || pip3 install PyYAML
python3 -c "import sqlite3" 2>/dev/null || echo "⚠️  SQLite3 not available - search indexing may not work"

# Try to install optional dependencies
echo "🎨 Installing optional dependencies..."
pip3 install pygments 2>/dev/null || echo "⚠️  Pygments not installed - syntax highlighting disabled"

# Check for Ollama
echo "🔍 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found: $(ollama --version 2>/dev/null || echo 'version unknown')"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✅ Ollama server is running"
        
        # List available models
        echo "📋 Available GPT OSS models:"
        ollama list | grep gpt-oss || echo "⚠️  No GPT OSS models found. Run: ollama pull gpt-oss:20b"
    else
        echo "⚠️  Ollama server is not running. Start with: ollama serve"
    fi
else
    echo "❌ Ollama not found. Please install from: https://ollama.ai"
    echo "   After installation, run: ollama pull gpt-oss:20b"
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p .gptoss-index
mkdir -p .backups
mkdir -p prepared-files

# Add tools to PATH
echo "🔗 Setting up PATH..."
SHELL_RC=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ -f "$HOME/.bash_profile" ]]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_RC" ]]; then
    # Check if already in PATH
    if ! grep -q "gptoss-tools" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# GPT OSS Tools" >> "$SHELL_RC"
        echo "export PATH=\"$TOOLS_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "✅ Added tools to PATH in $SHELL_RC"
        echo "   Run: source $SHELL_RC"
    else
        echo "✅ Tools already in PATH"
    fi
fi

# Create convenience aliases
echo "⚡ Creating convenience aliases..."
cat > gptoss << 'EOF'
#!/usr/bin/env bash
# GPT OSS Tools - Main Interface

TOOLS_DIR="/Users/cameronbrooks/gptoss-tools"

case "$1" in
    "glop"|"glob")
        shift
        "$TOOLS_DIR/glop" "$@"
        ;;
    "grep"|"search-text")
        shift
        "$TOOLS_DIR/grep" "$@"
        ;;
    "write"|"filewrite")
        shift
        "$TOOLS_DIR/filewrite" "$@"
        ;;
    "read"|"cat")
        shift
        "$TOOLS_DIR/read" "$@"
        ;;
    "search"|"index")
        shift
        "$TOOLS_DIR/search" "$@"
        ;;
    "ready"|"prepare")
        shift
        "$TOOLS_DIR/readymyfiles" "$@"
        ;;
    "status"|"info")
        echo "🤖 GPT OSS Tools Status"
        echo "Tools directory: $TOOLS_DIR"
        echo ""
        echo "Available tools:"
        echo "  glop       - File pattern matching"
        echo "  grep       - Text search"
        echo "  filewrite  - File creation/editing"
        echo "  read       - Smart file reading"
        echo "  search     - Content indexing"
        echo "  readymyfiles - File preparation"
        echo ""
        echo "Ollama status:"
        if command -v ollama &> /dev/null; then
            if curl -s http://localhost:11434/api/tags &> /dev/null; then
                echo "  ✅ Ollama server running"
                ollama list | grep gpt-oss | head -3 || echo "  ⚠️  No GPT OSS models found"
            else
                echo "  ⚠️  Ollama installed but not running"
            fi
        else
            echo "  ❌ Ollama not installed"
        fi
        ;;
    "help"|"--help"|"-h"|"")
        echo "🤖 GPT OSS Tools - AI Development Toolkit"
        echo ""
        echo "Usage: gptoss <tool> [arguments]"
        echo ""
        echo "Available tools:"
        echo "  glop       - Advanced file pattern matching"
        echo "  grep       - Powerful text search"
        echo "  filewrite  - File creation and editing utilities"
        echo "  read       - Smart file reading with syntax highlighting"
        echo "  search     - Content indexing and semantic search"
        echo "  readymyfiles - File preparation for AI workflows"
        echo ""
        echo "Special commands:"
        echo "  status     - Show system status"
        echo "  help       - Show this help"
        echo ""
        echo "Examples:"
        echo "  gptoss glop '*.py' --recursive"
        echo "  gptoss grep 'function' --include='*.js'"
        echo "  gptoss search index --directory=./src"
        echo "  gptoss ready prepare-for-ai --include='*.py'"
        echo ""
        echo "For tool-specific help, run: gptoss <tool> --help"
        ;;
    *)
        echo "❌ Unknown tool: $1"
        echo "Run 'gptoss help' for available tools"
        exit 1
        ;;
esac
EOF

chmod +x gptoss

# Test the tools
echo "🧪 Testing tools..."
echo "Testing glop..."
./glop "*.md" >/dev/null && echo "✅ glop working" || echo "❌ glop failed"

echo "Testing read..."
./read README.md --no-syntax --lines=5 >/dev/null && echo "✅ read working" || echo "❌ read failed"

echo "Testing filewrite..."
./filewrite templates >/dev/null && echo "✅ filewrite working" || echo "❌ filewrite failed"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Quick start:"
echo "  ./gptoss status              # Check system status"
echo "  ./gptoss glop '*.py' -r      # Find Python files"
echo "  ./gptoss search index        # Index current directory"
echo "  ./gptoss ready analyze-codebase --report  # Analyze codebase"
echo ""
echo "To use from anywhere, add this to your shell config:"
echo "  export PATH=\"$TOOLS_DIR:\$PATH\""
echo ""
echo "For GPT OSS model setup:"
echo "  ollama serve                 # Start Ollama server"
echo "  ollama pull gpt-oss:20b      # Download 20B model"
echo "  ollama pull gpt-oss:120b     # Download 120B model (optional)"
