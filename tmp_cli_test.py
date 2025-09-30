from typer.testing import CliRunner
from mnemosyne.main import app

runner = CliRunner()
for args in (
    ["github", "tools"],
    ["github", "call", "repos.list_for_authenticated_user"],
    ["agent-github", "list my repositories"],
):
    result = runner.invoke(app, args)
    print(f"command: mnemo {' '.join(args)}")
    print(f"exit: {result.exit_code}")
    if result.stdout:
        print("stdout:")
        print(result.stdout)
    if result.exception:
        print(f"exception: {result.exception}")
    print("-" * 40)
