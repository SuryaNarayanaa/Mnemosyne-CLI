from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .colors import PRIMARY_COLOR

console = Console()

def print_workflow_progress(step: str, progress: int = 50):
    """Print workflow progress with visual bar"""
    bar = "█" * (progress // 10) + "░" * ((100 - progress) // 10)
    progress_text = Text(f"[{bar}] {progress}% - {step}", style=PRIMARY_COLOR)

    panel = Panel(
        progress_text,
        border_style=PRIMARY_COLOR,
        title="[bold cyan]Workflow Progress[/bold cyan]",
        title_align="left"
    )
    console.print(panel)