from typing import Optional

from fastapi import status
from typer import Option, Typer
import typer

from pyre.cli.client import get_client


portfolio = Typer(add_completion=False)


@portfolio.command()
def worth(
    on: Optional[str] = Option(None, help="Date on which to retrieve gross worth"),
    pretty: bool = Option(False, "-p", "--pretty", help="Pretty print currency"),
):
    client = get_client("worth")
    response = client.get("/", params={"on": on} if on else None)
    if response.status_code == status.HTTP_200_OK:
        worth = response.json()["worth"]
        worth_str = f"{worth:.2f}"
        if pretty:
            worth_str = f"€{worth:,.0f}"

        typer.echo(worth_str)
    else:
        typer.echo(f"Error: {response.text}", err=True)
