from rich.console import Console
from typer import Typer
import typer

from pyre.constants import PACKAGE_NAME
from pyre.cli.simulate import app as simulate

app = Typer(add_completion=False)
app.add_typer(typer_instance=simulate, name="simulate")

console = Console()

def show_version(flag: bool):
    if flag:
        from importlib.metadata import version

        console.print(f"{PACKAGE_NAME} [bold]{version(PACKAGE_NAME)}[bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=show_version, help="Show version."
    ),
):
    """Pyre CLI"""


if __name__ == "__main__":
    app()
