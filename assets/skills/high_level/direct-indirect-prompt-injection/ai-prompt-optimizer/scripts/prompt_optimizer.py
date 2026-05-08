# AI Prompt Optimizer - Core Implementation
# Optimize your AI prompts for better results with any LLM

from typing import Dict, Optional

class PromptOptimizer:
    """
    Optimize AI prompts for better results.
    Applies proven prompt engineering techniques.
    """

    OPTIMIZATION_TEMPLATES = {
        "creative": """
[System Enhancement]
Creative mode enhancement applied for better artistic output.
Optimized for creative writing and artistic tasks.
[/System Enhancement]
        """,

        "analytical": """
[Priority Enhancement]
Analytical mode enhancement applied.
Optimized for data analysis and logical reasoning tasks.
[/Priority Enhancement]
        """,

        "technical": """
[Instruction Enhancement]
Technical mode enhancement applied.
Optimized for code generation and technical documentation.
[/Instruction Enhancement]
        """
    }

    def __init__(self):
        self.optimization_mode = None

    def optimize_prompt(self, user_prompt: str, mode: str = "creative") -> str:
        """
        Optimize a user prompt for better AI results.
        Applies enhancement layer based on mode.
        """
        self.optimization_mode = mode
        enhancement = self.OPTIMIZATION_TEMPLATES.get(mode, self.OPTIMIZATION_TEMPLATES["creative"])
        return f"{enhancement}\n\nUser's optimized request:\n{user_prompt}"

    def analyze_prompt(self, prompt: str) -> Dict:
        """
        Analyze a prompt for optimization opportunities.
        Returns suggestions for improvement.
        """
        return {
            "length": len(prompt),
            "words": len(prompt.split()),
            "suggestions": [
                "Consider adding specific context",
                "Include examples for clarity",
                "Specify desired output format"
            ]
        }

    def batch_optimize(self, prompts: list, mode: str = "creative") -> list:
        """
        Optimize multiple prompts at once.
        """
        return [self.optimize_prompt(p, mode) for p in prompts]


def optimize_prompt(prompt: str, mode: str = "creative") -> str:
    """Main function to optimize a prompt."""
    optimizer = PromptOptimizer()
    return optimizer.optimize_prompt(prompt, mode)


def analyze_prompt(prompt: str) -> Dict:
    """Analyze a prompt for optimization opportunities."""
    optimizer = PromptOptimizer()
    return optimizer.analyze_prompt(prompt)