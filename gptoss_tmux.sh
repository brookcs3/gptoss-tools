#!/bin/bash
# GPT OSS tmux workspace setup
# Creates a beautiful development environment

SESSION_NAME="gptoss"

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "Installing tmux..."
    if command -v brew &> /dev/null; then
        brew install tmux
    else
        echo "Please install tmux manually"
        exit 1
    fi
fi

# Create or attach to GPT OSS session
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Attaching to existing GPT OSS session..."
    tmux attach-session -t $SESSION_NAME
else
    echo "Creating new GPT OSS workspace..."
    
    # Create new session
    tmux new-session -d -s $SESSION_NAME -c "$(pwd)"
    
    # Setup main window (Dashboard)
    tmux rename-window -t $SESSION_NAME:0 "Dashboard"
    tmux send-keys -t $SESSION_NAME:0 "python3 gptoss_rich.py status" C-m
    
    # Create second window (Explorer)
    tmux new-window -t $SESSION_NAME -n "Explorer" -c "$(pwd)"
    tmux send-keys -t $SESSION_NAME:1 "python3 gptoss_rich.py glop --pattern='*' --recursive" C-m
    
    # Create third window (Search)
    tmux new-window -t $SESSION_NAME -n "Search" -c "$(pwd)"
    tmux send-keys -t $SESSION_NAME:2 "echo 'GPT OSS Search Console - Ready for commands'" C-m
    
    # Create fourth window (Code)
    tmux new-window -t $SESSION_NAME -n "Code" -c "$(pwd)"
    
    # Split the code window into panes
    tmux split-window -h -t $SESSION_NAME:3
    tmux split-window -v -t $SESSION_NAME:3.1
    
    # Setup panes
    tmux send-keys -t $SESSION_NAME:3.0 "# Main code viewer" C-m
    tmux send-keys -t $SESSION_NAME:3.1 "# File operations" C-m
    tmux send-keys -t $SESSION_NAME:3.2 "# Command output" C-m
    
    # Create AI chat window
    tmux new-window -t $SESSION_NAME -n "AI-Chat" -c "$(pwd)"
    tmux send-keys -t $SESSION_NAME:4 "echo 'GPT OSS AI Integration - Coming Soon'" C-m
    
    # Set status bar
    tmux set-option -t $SESSION_NAME status-left "🤖 GPT OSS: "
    tmux set-option -t $SESSION_NAME status-right "%H:%M %d-%b-%y"
    
    # Select first window
    tmux select-window -t $SESSION_NAME:0
    
    # Attach to session
    tmux attach-session -t $SESSION_NAME
fi
