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
