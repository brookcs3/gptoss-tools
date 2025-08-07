"""
Custom GPT OSS Theme
Override Textual's default colors with our own palette
"""

# Custom color definitions for GPT OSS
CUSTOM_THEME_CSS = """
App {
    /* Override Textual's default color variables */
    --primary: #0066cc;        /* Custom blue */
    --secondary: #4a90e2;      /* Lighter blue */
    --success: #28a745;        /* Custom green */
    --warning: #ff8c00;        /* Custom orange */
    --error: #dc3545;          /* Custom red */
    --accent: #17a2b8;         /* Custom cyan */
    
    /* Custom surface colors */
    --surface: #1a1a1a;        /* Dark background */
    --panel: #2d2d2d;          /* Panel background */
    
    /* Text colors */
    --text: #ffffff;           /* Main text */
    --text-muted: #888888;     /* Dimmed text */
    --text-disabled: #555555;  /* Disabled text */
}
"""

def get_custom_colors():
    """Get custom color palette as a dictionary"""
    return {
        'primary': '#0066cc',      # Blue for chat panel
        'secondary': '#4a90e2',    # Light blue for thinking panel  
        'success': '#28a745',      # Green for code viewer
        'warning': '#ff8c00',      # Orange for tools panel
        'error': '#dc3545',        # Red for errors
        'accent': '#17a2b8',       # Cyan for accents
    }
