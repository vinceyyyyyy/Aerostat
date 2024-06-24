import typer
from rich import print

from aerostat.core.loginer import get_aws_profile_credentials


def loggedin_check():
    try:
        get_aws_profile_credentials("aerostat")
    except KeyError:
        print(
            "[bold red]You are not logged in. Please run [bold blue]aerostat login[/bold blue] and try again.[/bold red]"
        )
        raise typer.Exit(1)
