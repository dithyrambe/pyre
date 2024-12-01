from typing import Optional

from httpx import Client
from typer import Typer
import pandas as pd
import typer
import yaml

from pyre.cli.helpers import render_table
from pyre.config import config


ORDERS_KEY = "orders"

order = Typer(add_completion=False)


def _get_client() -> Client:
    return Client(
        base_url=f"{config.PYRE_ENDPOINT}/v1/orders",
        headers={"X-API-Key": config.PYRE_API_KEY.get_secret_value()},
    )


@order.command()
def list(
    ticker: Optional[str] = typer.Option(
        None, "-t", "--ticker", help="Filter orders on a specific ticker"
    ),
    start_datetime: Optional[str] = typer.Option(None, help="Start date filter (inclusive)"),
    end_datetime: Optional[str] = typer.Option(None, help="End date filter (exclusive)"),
) -> None:
    """List all market orders passed"""
    client = _get_client()
    response = client.get(
        "/",
        params={
            "ticker": ticker,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
        },
    )
    orders = response.json()
    table = pd.DataFrame.from_records(orders).sort_values("id")
    render_table(table)


@order.command()
def register(
    id: int = typer.Option(..., help="Order id"),
    datetime: str = typer.Option(..., "-d", "--datetime", help="Datetime of the purchase"),
    ticker: str = typer.Option(..., "-t", "--ticker", help="Ticker symbol"),
    quantity: float = typer.Option(..., "-q", "--quantity", help="Number of units"),
    price: float = typer.Option(..., "-p", "--price", help="Price"),
    fees: float = typer.Option(0.0, "-f", "--fees", help="Broker fee"),
) -> None:
    """Register a passed market order."""
    client = _get_client()

    order = {
        "id": id,
        "datetime": datetime,
        "ticker": ticker,
        "quantity": quantity,
        "price": price,
        "fees": fees,
    }
    client.post("/", json=order)


@order.command()
def bulk(file: str) -> None:
    """Insert stock market orders in bulk from yaml"""
    client = _get_client()

    with open(file) as f:
        data = yaml.safe_load(f)

    client.post("/bulk", json=data[ORDERS_KEY])


@order.command()
def delete(id: int) -> None:
    """Delete an order by its ID"""
    client = _get_client()
    client.delete(f"/{id}")


@order.command()
def dump(
    output: Optional[str] = typer.Option(
        None, "-o", "--output", help="Output location to dump yaml"
    ),
) -> None:
    """Dump all orders (for backup purposes)"""
    client = _get_client()

    response = client.get("/")
    orders = response.json()
    data = {ORDERS_KEY: orders}
    if output:
        with open(output, "w") as f:
            yaml.safe_dump(data, f)
    else:
        typer.echo(yaml.safe_dump(data))
