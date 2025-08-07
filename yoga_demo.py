#!/usr/bin/env python3
"""
Yoga-Style Layout Engine Demonstration
Shows how Flexbox-inspired layouts work like Meta's Yoga
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum

class FlexDirection(Enum):
    ROW = "row"
    COLUMN = "column"

class JustifyContent(Enum):
    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"

class AlignItems(Enum):
    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"
    STRETCH = "stretch"

@dataclass
class YogaNode:
    """
    Yoga-style layout node (like Meta's Yoga)
    Demonstrates CSS Flexbox concepts in terminal layouts
    """
    # Content
    content: str = ""
    
    # Layout properties (like CSS Flexbox)
    flex_direction: FlexDirection = FlexDirection.COLUMN
    justify_content: JustifyContent = JustifyContent.FLEX_START
    align_items: AlignItems = AlignItems.FLEX_START
    
    # Size properties
    width: Optional[int] = None
    height: Optional[int] = None
    flex_grow: float = 0
    flex_shrink: float = 1
    flex_basis: Optional[int] = None
    
    # Spacing
    margin: int = 0
    padding: int = 1
    
    # Styling
    border: bool = True
    border_char: str = "│"
    corner_char: str = "┌"
    
    # Children
    children: List['YogaNode'] = None
    
    # Computed properties (set during layout)
    computed_x: int = 0
    computed_y: int = 0
    computed_width: int = 0
    computed_height: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def add_child(self, child: 'YogaNode') -> 'YogaNode':
        """Add a child node (fluent interface)"""
        self.children.append(child)
        return self
    
    def calculate_layout(self, available_width: int, available_height: int):
        """
        Calculate layout using Flexbox algorithm (simplified)
        This mimics what Meta's Yoga does
        """
        # Set initial dimensions
        self.computed_width = self.width or available_width
        self.computed_height = self.height or available_height
        
        if not self.children:
            return
        
        # Calculate child dimensions based on flex direction
        if self.flex_direction == FlexDirection.ROW:
            self._layout_row(available_width, available_height)
        else:
            self._layout_column(available_width, available_height)
    
    def _layout_row(self, available_width: int, available_height: int):
        """Layout children in a row (horizontal)"""
        total_flex_grow = sum(child.flex_grow for child in self.children)
        remaining_width = available_width - (len(self.children) * 2)  # Account for padding
        
        current_x = self.padding
        
        for child in self.children:
            # Calculate child width
            if child.width:
                child_width = child.width
            elif total_flex_grow > 0 and child.flex_grow > 0:
                child_width = int((remaining_width * child.flex_grow) / total_flex_grow)
            else:
                child_width = remaining_width // len(self.children)
            
            # Set child position
            child.computed_x = current_x
            child.computed_y = self.padding
            child.computed_width = child_width
            child.computed_height = available_height - (2 * self.padding)
            
            # Recursively layout child
            child.calculate_layout(child_width, child.computed_height)
            
            current_x += child_width + self.padding
    
    def _layout_column(self, available_width: int, available_height: int):
        """Layout children in a column (vertical)"""
        total_flex_grow = sum(child.flex_grow for child in self.children)
        remaining_height = available_height - (len(self.children) * 2)  # Account for padding
        
        current_y = self.padding
        
        for child in self.children:
            # Calculate child height
            if child.height:
                child_height = child.height
            elif total_flex_grow > 0 and child.flex_grow > 0:
                child_height = int((remaining_height * child.flex_grow) / total_flex_grow)
            else:
                child_height = remaining_height // len(self.children)
            
            # Set child position
            child.computed_x = self.padding
            child.computed_y = current_y
            child.computed_width = available_width - (2 * self.padding)
            child.computed_height = child_height
            
            # Recursively layout child
            child.calculate_layout(child.computed_width, child_height)
            
            current_y += child_height + self.padding
    
    def render(self, terminal_width: int = 80, terminal_height: int = 25) -> str:
        """Render the layout to terminal output"""
        # Calculate layout first
        self.calculate_layout(terminal_width, terminal_height)
        
        # Create terminal grid
        grid = [[' ' for _ in range(terminal_width)] for _ in range(terminal_height)]
        
        # Render this node and children
        self._render_node(grid, terminal_width, terminal_height)
        
        # Convert grid to string
        return '\n'.join(''.join(row) for row in grid)
    
    def _render_node(self, grid: List[List[str]], terminal_width: int, terminal_height: int):
        """Render this node onto the grid"""
        x, y = self.computed_x, self.computed_y
        w, h = self.computed_width, self.computed_height
        
        # Ensure bounds
        x = max(0, min(x, terminal_width - 1))
        y = max(0, min(y, terminal_height - 1))
        w = min(w, terminal_width - x)
        h = min(h, terminal_height - y)
        
        # Draw border if enabled
        if self.border and w > 2 and h > 2:
            # Top and bottom borders
            for i in range(w):
                if y < terminal_height and x + i < terminal_width:
                    grid[y][x + i] = '─'
                if y + h - 1 < terminal_height and x + i < terminal_width:
                    grid[y + h - 1][x + i] = '─'
            
            # Left and right borders  
            for i in range(h):
                if y + i < terminal_height and x < terminal_width:
                    grid[y + i][x] = '│'
                if y + i < terminal_height and x + w - 1 < terminal_width:
                    grid[y + i][x + w - 1] = '│'
            
            # Corners
            if y < terminal_height and x < terminal_width:
                grid[y][x] = '┌'
            if y < terminal_height and x + w - 1 < terminal_width:
                grid[y][x + w - 1] = '┐'
            if y + h - 1 < terminal_height and x < terminal_width:
                grid[y + h - 1][x] = '└'
            if y + h - 1 < terminal_height and x + w - 1 < terminal_width:
                grid[y + h - 1][x + w - 1] = '┘'
        
        # Draw content
        if self.content and w > 2 and h > 2:
            lines = self.content.split('\n')
            for line_idx, line in enumerate(lines[:h-2]):  # Leave space for borders
                if y + 1 + line_idx < terminal_height:
                    for char_idx, char in enumerate(line[:w-2]):  # Leave space for borders
                        if x + 1 + char_idx < terminal_width:
                            grid[y + 1 + line_idx][x + 1 + char_idx] = char
        
        # Render children
        for child in self.children:
            child.computed_x += x
            child.computed_y += y
            child._render_node(grid, terminal_width, terminal_height)


def create_gpt_oss_yoga_layout():
    """
    Create a GPT OSS layout using Yoga-style nodes
    This demonstrates how Claude Code might structure its layouts
    """
    
    # Main container (like Claude Code's main window)
    root = YogaNode(
        flex_direction=FlexDirection.COLUMN,
        border=True,
        content=""
    )
    
    # Header section
    header = YogaNode(
        content="🤖 GPT OSS Tools - Yoga Layout Demo",
        height=3,
        border=True,
        flex_grow=0
    )
    
    # Main content area (horizontal split)
    main_content = YogaNode(
        flex_direction=FlexDirection.ROW,
        flex_grow=1,
        border=False
    )
    
    # Left sidebar (file explorer + search)
    sidebar = YogaNode(
        flex_direction=FlexDirection.COLUMN,
        width=30,
        border=True,
        flex_grow=0
    )
    
    # File explorer
    file_explorer = YogaNode(
        content="📁 Files\n" + "\n".join([
            "├── gptoss_rich.py",
            "├── simple_tui.py", 
            "├── yoga_demo.py",
            "└── config.yaml"
        ]),
        flex_grow=1,
        border=True
    )
    
    # Search panel
    search_panel = YogaNode(
        content="🔍 Search\n\nPattern: *.py\nResults: 5 files",
        height=8,
        border=True,
        flex_grow=0
    )
    
    # Right content area (code viewer + terminal)
    content_area = YogaNode(
        flex_direction=FlexDirection.COLUMN,
        flex_grow=1,
        border=False
    )
    
    # Code viewer
    code_viewer = YogaNode(
        content="📄 Code Viewer\n\ndef yoga_layout():\n    # This is how Yoga\n    # calculates layouts\n    return 'flexible!'",
        flex_grow=2,
        border=True
    )
    
    # Terminal/command area
    terminal = YogaNode(
        content="💻 Terminal\n$ ./gptoss status\n✅ All tools ready",
        height=10,
        border=True,
        flex_grow=0
    )
    
    # Footer
    footer = YogaNode(
        content="q:Quit | r:Refresh | h:Help",
        height=3,
        border=True,
        flex_grow=0
    )
    
    # Build the tree (like constructing React components)
    sidebar.add_child(file_explorer).add_child(search_panel)
    content_area.add_child(code_viewer).add_child(terminal)
    main_content.add_child(sidebar).add_child(content_area)
    root.add_child(header).add_child(main_content).add_child(footer)
    
    return root


def demonstrate_yoga_concepts():
    """Demonstrate key Yoga/Flexbox concepts"""
    
    print("🧘 Yoga Layout Engine Demonstration")
    print("=" * 50)
    print()
    
    print("Key Concepts:")
    print("1. **Flex Direction**: row (horizontal) vs column (vertical)")
    print("2. **Flex Grow**: how much space a child should take")
    print("3. **Flex Basis**: initial size before growing/shrinking")
    print("4. **Justify Content**: alignment along main axis")
    print("5. **Align Items**: alignment along cross axis")
    print()
    
    # Create and render the layout
    layout = create_gpt_oss_yoga_layout()
    rendered = layout.render(80, 25)
    
    print("GPT OSS Interface using Yoga-style Layout:")
    print("─" * 80)
    print(rendered)
    print("─" * 80)
    print()
    
    print("Layout Tree Structure:")
    print("```")
    print("root (column)")
    print("├── header (fixed height: 3)")
    print("├── main_content (row, flex: 1)")
    print("│   ├── sidebar (column, width: 30)")
    print("│   │   ├── file_explorer (flex: 1)")
    print("│   │   └── search_panel (height: 8)")
    print("│   └── content_area (column, flex: 1)")
    print("│       ├── code_viewer (flex: 2)")
    print("│       └── terminal (height: 10)")
    print("└── footer (fixed height: 3)")
    print("```")
    print()
    
    print("This is similar to how Claude Code structures its layout!")
    print("Each component knows its constraints and grows/shrinks accordingly.")


if __name__ == "__main__":
    demonstrate_yoga_concepts()
