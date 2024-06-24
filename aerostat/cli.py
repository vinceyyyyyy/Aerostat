from typing import Optional

import questionary
import typer
from rich import print

from aerostat import __app_name__, __version__
from aerostat.core import deploy_to_aws, aws_login
from aerostat.core.checks import loggedin_check
from aerostat.core.utils import get_system_dependencies

app = typer.Typer()


@app.command()
def login() -> None:
    """Configure AWS credentials for Aerostat to use.

    This command create or modifies ~/.aws/credentials, creating a new AWS profile named "Aerostat" if it does not exist.
    """
    profiles = []
    cred_file = None

    try:
        cred_file = aws_login.get_aws_credential_file()
        profiles = cred_file.sections()
    except FileNotFoundError:
        pass

    if len(profiles) > 0:
        if "aerostat" in profiles:
            print("[bold green]Aerostat already logged in.[/bold green]")
            return

        use_existing = questionary.confirm(
            "Existing AWS profiles detected, use existing ones?"
        ).ask()
        # if using existing profile, copy profile to aerostat
        if use_existing:
            profile = questionary.select(
                "Select from existing AWS profile to use", choices=profiles
            ).ask()  # returns value of selection
            aws_login.create_aws_profile(
                "aerostat",
                cred_file[profile]["aws_access_key_id"],
                cred_file[profile]["aws_secret_access_key"],
            )
            return

    if not cred_file or len(profiles) == 0:
        print(
            "[bold red]No AWS profile found. Please create AWS profile with access key first.[/bold red]"
        )
    else:
        print("[bold red]Input AWS credentials for Aerostat[/bold red]")
    aws_login.prompted_create_aws_profile()

    print(
        "[bold green]AWS credentials for Aerostat configured successfully.[/bold green]"
    )


@app.command()
def deploy(
    local: bool = typer.Option(
        False,
        "--local",
        help="Deploy locally for testing. Default is to deploy to AWS Lambda.",
    ),
    model_path: str = typer.Option(
        ..., "--model-path", prompt="Model pickle file path"
    ),
    input_columns: str = typer.Option(
        ...,
        "--input-columns",
        prompt="""Model input columns - type in python list format like ["col_1", "col_2", ...]""",
    ),
    python_dependencies: str = typer.Option(
        ...,
        "--python-dependencies",
        prompt="""Machine Learning library used for the model (type in as pip installable name, e.g. scikit-learn if sklearn is used)""",
    ),
    project_name: str = typer.Option(
        "Aerostat", "--project-name", prompt="Name of the project"
    ),
):
    """Deploy model to AWS Lambda.

    This command uses Docker to build image locally, and deploys to AWS Lambda with Serverless Framework.
    It will blow up if Docker Desktop is not running.
    """
    try:
        input_columns = eval(input_columns)
    except Exception:
        raise Exception(
            """Input column list is not valid. Please input valid python list as ["col_1", "col_2", ...]"""
        )

    python_dependencies = python_dependencies.split(" ")

    if local:
        print("[bold green]Deploying locally...[/bold green]")

    print("[bold green]Deploying to AWS Lambda...[/bold green]")
    loggedin_check()
    return deploy_to_aws(
        model_path=model_path,
        input_columns=input_columns,
        python_dependencies=python_dependencies,
        system_dependencies=get_system_dependencies(python_dependencies),
        project_name=project_name,
    )
    # TODO: capture returned api endpoint


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return
