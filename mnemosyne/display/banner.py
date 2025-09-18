from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from .colors import PRIMARY_COLOR, SECONDARY_COLOR, NEUTRAL_COLOR, ACCENT_1

console = Console()

def print_banner():
    """Print a cool ASCII banner for Mnemosyne CLI"""
    banner = Text()
    banner.append("███╗░░░███╗███╗░░██╗███████╗███╗░░░███╗░█████╗░░██████╗██╗░░░██╗███╗░░██╗███████╗\n", style=NEUTRAL_COLOR)
    banner.append("████╗░████║████╗░██║██╔════╝████╗░████║██╔══██╗██╔════╝╚██╗░██╔╝████╗░██║██╔════╝\n", style=NEUTRAL_COLOR)
    banner.append("██╔████╔██║██╔██╗██║█████╗░░██╔████╔██║██║░░██║╚█████╗░░╚████╔╝░██╔██╗██║█████╗░░\n", style=NEUTRAL_COLOR)
    banner.append("██║╚██╔╝██║██║╚████║██╔══╝░░██║╚██╔╝██║██║░░██║░╚═══██╗░░╚██╔╝░░██║╚████║██╔══╝░░\n", style=NEUTRAL_COLOR)
    banner.append("██║░╚═╝░██║██║░╚███║███████╗██║░╚═╝░██║╚█████╔╝██████╔╝░░░██║░░░██║░╚███║███████╗\n", style=NEUTRAL_COLOR)
    banner.append("╚═╝░░░░░╚═╝╚═╝░░╚══╝╚══════╝╚═╝░░░░░╚═╝░╚════╝░╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝╚══════╝\n", style=NEUTRAL_COLOR)

    subtitle = Text("AI Assistant CLI for Multi-Agent Orchestration", style=NEUTRAL_COLOR)

    panel = Panel(
    Align.center(Columns([banner, subtitle], align="center")),
    border_style=ACCENT_1,
    title=f"[{ACCENT_1} bold]Mnemosyne CLI[/]",
    title_align="center"
)

    console.print(panel)