import typer
from .display import print_banner, print_success_message

app = typer.Typer()


@app.callback()
def callback():
    """
    Mnemosyne: AI Assistant CLI for multi-agent orchestration
    """
    print_banner()
    print_success_message("Data store initialized.")


@app.command()
def help():
    """
    List available features and commands
    """
    print_banner()
    typer.echo("• init - Initialize data store structure for agents and workflows")
    typer.echo("• agent-create - Create a new AI agent")
    typer.echo("• workflow-run - Execute a workflow from YAML file")
    typer.echo("• list - List agents or workflows")
    typer.echo("• export - Export configurations to file")
    typer.echo("• import-config - Import configurations from file")
    typer.echo("• dashboard - Launch Textual TUI dashboard")
    typer.echo("• help - Show this list of features")
    typer.echo("\nUse 'python -m mnemosyne <command> --help' for more details on each command.")


    
    