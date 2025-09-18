from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .colors import ACCENT_1, ACCENT_2

console = Console()

def print_workflow_progress(step: str, progress: int = 50):
    """Print workflow progress with visual bar"""
    bar = "█" * (progress // 10) + "░" * ((100 - progress) // 10)
    progress_text = Text(f"[{bar}] {progress}% - {step}", style=ACCENT_1)

    panel = Panel(
        progress_text,
        border_style=ACCENT_1,
title=f"[{ACCENT_2} bold]Workflow Progress[/]",
        title_align="left"
    )
    console.print(panel)