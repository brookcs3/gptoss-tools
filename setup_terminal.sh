#!/bin/bash
# Terminal Environment Setup for GPT OSS
# Run this to improve your terminal experience

echo "🚀 Setting up enhanced terminal environment..."

# Check current terminal
echo "Current terminal: $TERM"
echo "Terminal program: $TERM_PROGRAM"

# Set better TERM if needed
if [[ -z "$TERM" || "$TERM" == "dumb" ]]; then
    echo "Setting TERM=xterm-256color"
    export TERM=xterm-256color
fi

# Add to your shell profile
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_CONFIG" ]]; then
    echo "# GPT OSS Terminal Environment" >> "$SHELL_CONFIG"
    echo "export TERM=xterm-256color" >> "$SHELL_CONFIG"
    echo "export COLORTERM=truecolor" >> "$SHELL_CONFIG"
    echo "export GPT_OSS_TOOLS_PATH=\"$(pwd)\"" >> "$SHELL_CONFIG"
    echo ""
    echo "✅ Added environment variables to $SHELL_CONFIG"
    echo "   Run: source $SHELL_CONFIG"
fi

# Test color support
echo -e "\n🎨 Color test:"
echo -e "\033[31mRed\033[0m \033[32mGreen\033[0m \033[33mYellow\033[0m \033[34mBlue\033[0m \033[35mMagenta\033[0m \033[36mCyan\033[0m"

# Create launch script
cat > gptoss_launch.sh << 'EOF'
#!/bin/bash
# GPT OSS Enhanced Launcher

export TERM=xterm-256color
export COLORTERM=truecolor

echo "🤖 GPT OSS Tools Launcher"
echo "========================="
echo ""

PS3="Select an interface: "
options=("Rich Interactive Mode" "Status Dashboard" "File Explorer" "Direct Command" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Rich Interactive Mode")
            python3 gptoss_rich.py interactive
            break
            ;;
        "Status Dashboard")
            python3 gptoss_rich.py status
            break
            ;;
        "File Explorer")
            echo "Enter pattern (e.g., *.py):"
            read pattern
            python3 gptoss_rich.py glop --pattern="$pattern" --recursive
            break
            ;;
        "Direct Command")
            echo "Available commands: status, glop, search, read"
            echo "Enter command:"
            read cmd
            python3 gptoss_rich.py $cmd
            break
            ;;
        "Quit")
            echo "👋 Goodbye!"
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
EOF

chmod +x gptoss_launch.sh
echo "✅ Created gptoss_launch.sh - your new launcher!"
