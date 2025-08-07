#!/usr/bin/env python3
"""
ChatPanel class for GPT OSS TUI
Handles chat messages with proper scrolling
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Label, Static, Button, Input
from textual.reactive import reactive
from datetime import datetime


class ChatPanel(Container):
    """Chat interface panel with proper scrolling"""

    messages = reactive([])

    def __init__(self):
        super().__init__()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "gpt-oss:20b"

    def compose(self) -> ComposeResult:
        yield Label("🤖 GPT OSS Chat", classes="panel-header")

        with ScrollableContainer(id="chat_content", classes="chat-scroll"):
            yield Static("Welcome to GPT OSS! Ask me anything or request tool operations.", 
                        classes="welcome-message")

        with Horizontal(classes="chat-input-area"):
            yield Input(placeholder="Ask GPT OSS anything...", id="chat_input")
            yield Button("Send", id="send_btn", variant="primary")
            yield Button("Tools", id="tools_btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            self.send_message()
        elif event.button.id == "tools_btn":
            self.show_tools_help()

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "chat_input":
            self.send_message()

    def add_message(self, role: str, content: str):
        """Add a message to the chat history with proper scrolling"""
        if not content.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        
        chat_container = self.query_one("#chat_content", ScrollableContainer)

        # Remove welcome message if it exists
        if chat_container.children and "Welcome to GPT OSS" in str(chat_container.children[0]):
            chat_container.children[0].remove()

        # Create role header
        role_icon = "🤖" if role == "assistant" else "👤"
        role_style = "dim" if role == "assistant" else "bold"
        
        role_widget = Static(f"{role_icon} {role.title()} {timestamp}")
        role_widget.add_class(f"chat-role {role_style}")
        chat_container.mount(role_widget)

        # Create content
        content_widget = Static(content)
        content_widget.add_class("chat-content")
        chat_container.mount(content_widget)

        # Auto-scroll to bottom
        chat_container.scroll_end()

    def send_message(self):
        """Send user message and get AI response"""
        chat_input = self.query_one("#chat_input", Input)
        user_message = chat_input.value.strip()

        if not user_message:
            return

        # Add user message to chat
        self.add_message("user", user_message)
        chat_input.value = ""

        # Get AI response
        self.get_ai_response(user_message)

    def get_ai_response(self, user_message: str):
        """Get response from GPT OSS model"""
        try:
            # Show typing indicator
            self.add_message("assistant", "🤔 Thinking...")

            # Call Ollama API (same logic as before)
            response = self._call_ollama(user_message)

            # Remove typing indicator and add real response
            chat_container = self.query_one("#chat_content", ScrollableContainer)
            if chat_container.children and "🤔 Thinking..." in str(chat_container.children[-1]):
                chat_container.children[-1].remove()
                chat_container.children[-1].remove()  # Remove role header too

            self.add_message("assistant", response)

        except Exception as e:
            # Remove typing indicator
            chat_container = self.query_one("#chat_content", ScrollableContainer)
            if chat_container.children and "🤔 Thinking..." in str(chat_container.children[-1]):
                chat_container.children[-1].remove()
                chat_container.children[-1].remove()

            error_msg = f"❌ Error: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"
            self.add_message("assistant", error_msg)

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API synchronously"""
        import requests

        system_prompt = """You are GPT OSS, an AI assistant integrated into a powerful development toolkit. You can help with:

1. **File Operations**: Finding, reading, and analyzing files
2. **Code Search**: Searching through codebases and finding patterns
3. **Project Analysis**: Understanding project structure and dependencies
4. **Tool Execution**: Running development tools and commands

Available tools in this environment:
- `glop <pattern>` - Find files by pattern (e.g., "*.py", "*.js")
- `grep <query>` - Search file contents for text patterns
- `search <query>` - Semantic search through indexed files
- `read <file>` - Display file contents with syntax highlighting
- `readymyfiles` - Prepare files for AI analysis
- `filewrite` - Create and edit files

When users ask you to perform actions, suggest specific tool commands or execute them if requested. Be helpful, practical, and focus on developer productivity.

User message: """

        data = {
            "model": self.model,
            "prompt": system_prompt + prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 4096
            }
        }

        response = requests.post(self.ollama_url, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()

        # Extract thinking and send to ThinkingPanel
        thinking = result.get("thinking", "")
        if thinking.strip():
            thinking_panel = self.app.query_one("#thinking_panel")
            if hasattr(thinking_panel, 'add_thinking'):
                thinking_panel.add_thinking(thinking)

        return result.get("response", "No response generated")

    def show_tools_help(self):
        """Show available tools"""
        tools_help = """## Available Tools

**File Operations:**
- `glop "*.py"` - Find Python files
- `read config.yaml` - View file contents
- `grep "function"` - Search for text in files

**Search & Analysis:**
- `search "authentication"` - Semantic search
- `readymyfiles analyze-codebase` - Project analysis

**Examples:**
- "Find all Python files in this project"
- "Search for authentication code"
- "Show me the config file"
- "Analyze this codebase structure"

Just ask naturally - I'll suggest the right tools!"""

        self.add_message("assistant", tools_help)

    def clear_chat(self):
        """Clear all chat content"""
        chat_container = self.query_one("#chat_content", ScrollableContainer)
        chat_container.remove_children()
        chat_container.mount(Static("Welcome to GPT OSS! Ask me anything or request tool operations.", 
                                  classes="welcome-message"))
