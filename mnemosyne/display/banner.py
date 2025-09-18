from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from .colors import PRIMARY_COLOR, SECONDARY_COLOR, NEUTRAL_COLOR

console = Console()

def print_banner():
    """Print a cool ASCII banner for Mnemosyne CLI"""
    banner = Text()
    banner.append("███╗░░░███╗███╗░░██╗███████╗███╗░░░███╗░█████╗░░██████╗██╗░░░██╗███╗░░██╗███████╗\n", style=PRIMARY_COLOR)
    banner.append("████╗░████║████╗░██║██╔════╝████╗░████║██╔══██╗██╔════╝╚██╗░██╔╝████╗░██║██╔════╝\n", style=SECONDARY_COLOR)
    banner.append("██╔████╔██║██╔██╗██║█████╗░░██╔████╔██║██║░░██║╚█████╗░░╚████╔╝░██╔██╗██║█████╗░░\n", style=PRIMARY_COLOR)
    banner.append("██║╚██╔╝██║██║╚████║██╔══╝░░██║╚██╔╝██║██║░░██║░╚═══██╗░░╚██╔╝░░██║╚████║██╔══╝░░\n", style=SECONDARY_COLOR)
    banner.append("██║░╚═╝░██║██║░╚███║███████╗██║░╚═╝░██║╚█████╔╝██████╔╝░░░██║░░░██║░╚███║███████╗\n", style=PRIMARY_COLOR)
    banner.append("╚═╝░░░░░╚═╝╚═╝░░╚══╝╚══════╝╚═╝░░░░░╚═╝░╚════╝░╚═════╝░░░░╚═╝░░░╚═╝░░╚══╝╚══════╝\n", style=SECONDARY_COLOR)

    subtitle = Text("AI Assistant CLI for Multi-Agent Orchestration", style=NEUTRAL_COLOR)
    subtitle.stylize(style=PRIMARY_COLOR, start=0, end=2)
    subtitle.stylize(style=SECONDARY_COLOR, start=3, end=10)

    panel = Panel(
        Align.center(Columns([banner, subtitle], align="center")),
        border_style=PRIMARY_COLOR,
        title="[bold cyan]Mnemosyne CLI[/bold cyan]",
        title_align="center"
    )
    console.print(panel)