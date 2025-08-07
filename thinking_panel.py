#!/usr/bin/env python3
"""
ThinkingPanel class for GPT OSS TUI
Shows AI reasoning process in real-time
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Label, Static, Button, Markdown
from textual.reactive import reactive
from datetime import datetime


class ThinkingPanel(Container):
    """AI Thinking Process Panel - Shows model's reasoning in real-time"""

    current_thinking = reactive("")
    thinking_history = reactive([])

    def compose(self) -> ComposeResult:
        yield Label("🧠 AI Thinking Process", classes="panel-header")
        
        with Horizontal(classes="thinking-controls"):
            yield Static("💭 Model reasoning appears here", id="thinking_status", classes="thinking-info")
            yield Button("Clear", id="clear_thinking", variant="warning", classes="small-btn")

        with ScrollableContainer(id="thinking_content", classes="thinking-scroll"):
            yield Static("🤔 Waiting for AI to think...", classes="thinking-placeholder")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "clear_thinking":
            self.clear_thinking()

    def add_thinking(self, thinking_text: str, timestamp: str = None):
        """Add new thinking content to the panel"""
        if not thinking_text.strip():
            return
            
        timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        
        thinking_container = self.query_one("#thinking_content", ScrollableContainer)
        
        # Remove placeholder if it exists
        if thinking_container.children and "Waiting for AI" in str(thinking_container.children[0]):
            thinking_container.children[0].remove()
        
        # Create thinking entry
        thinking_widget = Static(f"💭 {timestamp}")
        thinking_widget.add_class("thinking-timestamp")
        thinking_container.mount(thinking_widget)
        
        content_widget = Markdown(thinking_text)
        content_widget.add_class("thinking-content")  
        thinking_container.mount(content_widget)
        
        # Auto-scroll to bottom
        thinking_container.scroll_end()
        
        # Update status
        status = self.query_one("#thinking_status", Static)
        status.update(f"💭 Latest: {thinking_text[:50]}...")

    def clear_thinking(self):
        """Clear all thinking content"""
        thinking_container = self.query_one("#thinking_content", ScrollableContainer)
        thinking_container.remove_children()
        thinking_container.mount(Static("🤔 Waiting for AI to think...", classes="thinking-placeholder"))
        
        status = self.query_one("#thinking_status", Static)
        status.update("💭 Model reasoning appears here")

    def get_all_thinking_text(self) -> str:
        """Get all thinking text for copying"""
        thinking_container = self.query_one("#thinking_content", ScrollableContainer)
        all_text = []
        
        for child in thinking_container.children:
            if hasattr(child, 'renderable'):
                # Get text from Markdown widgets
                if hasattr(child.renderable, 'markup'):
                    all_text.append(str(child.renderable.markup))
                else:
                    all_text.append(str(child.renderable))
            elif hasattr(child, 'value'):
                # Get text from Static widgets
                all_text.append(str(child.value))
            else:
                # Fallback to string representation
                all_text.append(str(child))
        
        # Join with newlines and clean up
        full_text = "\n".join(all_text)
        # Remove placeholder text
        if "Waiting for AI to think" in full_text:
            return ""
        
        return full_text.strip()
