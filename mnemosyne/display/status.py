from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .colors import PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS, ERROR, WARNING, MAIN_TEXT, ACCENT_1

console = Console()

def print_agent_status(agent_name: str, status: str = "active"):
    """Print agent status with cool formatting"""
    if status == "active":
        status_icon = "🟢"
        color = SUCCESS
        title_color = SUCCESS
    else:
        status_icon = "🔴"
        color = ERROR
        title_color = ERROR

    status_text = Text(f"{status_icon} Agent '{agent_name}' is {status}", style=color)

    panel = Panel(
        status_text,
        border_style=ACCENT_1,
        title=f"[{title_color} bold]Agent Status[/{title_color}]",
        title_align="left"
    )
    console.print(panel)

def print_success_message(message: str):
    """Print success message with checkmark"""
    success_text = Text(f"✅ {message}", style=SUCCESS)
    console.print(success_text)

def print_error_message(message: str):
    """Print error message with cross"""
    error_text = Text(f"❌ {message}", style=ERROR)
    console.print(error_text)

def print_info_message(message: str):
    """Print info message with info icon"""
    info_text = Text(f"ℹ️  {message}", style=MAIN_TEXT)
    console.print(info_text)