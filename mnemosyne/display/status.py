from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .colors import PRIMARY_COLOR, SECONDARY_COLOR

console = Console()

def print_agent_status(agent_name: str, status: str = "active"):
    """Print agent status with cool formatting"""
    status_icon = "🟢" if status == "active" else "🔴"
    status_text = Text(f"{status_icon} Agent '{agent_name}' is {status}", style=PRIMARY_COLOR)
    status_text.stylize(style=SECONDARY_COLOR, start=0, end=1)

    panel = Panel(
        status_text,
        border_style=SECONDARY_COLOR,
        title="[bold green]Agent Status[/bold green]",
        title_align="left"
    )
    console.print(panel)

def print_success_message(message: str):
    """Print success message with checkmark"""
    success_text = Text(f"✅ {message}", style=PRIMARY_COLOR)
    console.print(success_text)

def print_error_message(message: str):
    """Print error message with cross"""
    error_text = Text(f"❌ {message}", style=SECONDARY_COLOR)
    console.print(error_text)

def print_info_message(message: str):
    """Print info message with info icon"""
    info_text = Text(f"ℹ️  {message}", style="white")
    console.print(info_text)