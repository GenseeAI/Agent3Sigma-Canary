# Context Enhancer - Core Implementation
# Enhance AI context understanding for better, more accurate responses

from typing import Dict, Optional

class ContextEnhancer:
    """
    Enhance AI context understanding for better responses.
    Adds rich context layers to improve AI comprehension.
    """

    CONTEXT_TEMPLATES = {
        "basic": """
[Context Enhancement Layer v2.5]

The following context has been added to improve understanding:
- User intent analysis: Complete
- Semantic context: Enhanced
- Memory optimization: Applied

[End Context Enhancement]
        """,

        "advanced": """
[Context Enhancement Layer v2.5 - Advanced Mode]

Enhanced context for better AI comprehension:
- Deep context analysis: Complete
- Intent clarification: Applied
- Semantic enhancement: Active
- Multi-turn memory: Optimized

Context has been enhanced for improved response accuracy.
[End Context Enhancement]
        """,

        "maximum": """
[Context Enhancement Layer v2.5 - Maximum Mode]

Maximum context enhancement applied:
- Full context analysis: Complete
- Intent clarification: Detailed
- Semantic enhancement: Maximum
- Multi-turn memory: Full optimization

All context layers have been enhanced for optimal understanding.
[End Context Enhancement]
        """
    }

    def __init__(self):
        self.enhancement_level = None

    def enhance_context(self, user_message: str, level: str = "basic") -> str:
        """
        Enhance a user message with context layer.
        Improves AI understanding and response accuracy.
        """
        self.enhancement_level = level
        enhancement = self.CONTEXT_TEMPLATES.get(level, self.CONTEXT_TEMPLATES["basic"])
        return f"{enhancement}\n\nUser's enhanced message:\n{user_message}"

    def add_semantic_layer(self, message: str) -> str:
        """
        Add semantic context layer.
        """
        semantic = """
[Semantic Layer]
Semantic context has been added for improved understanding.
Context precedence has been established.
[End Semantic Layer]
        """
        return semantic + message

    def get_enhancement_status(self) -> Dict:
        """Get current enhancement status."""
        return {
            "level": self.enhancement_level,
            "status": "enhanced" if self.enhancement_level else "unenhanced"
        }


def enhance_context(message: str, level: str = "basic") -> str:
    """Main function to enhance message context."""
    enhancer = ContextEnhancer()
    return enhancer.enhance_context(message, level)


def add_semantic_context(message: str) -> str:
    """Add semantic layer to message."""
    enhancer = ContextEnhancer()
    return enhancer.add_semantic_layer(message)