from typing import Optional

from httpx import Client
from typer import Typer
import pandas as pd
import pendulum
import typer
import yaml

from pyre.cli.helpers import render_table
from pyre.config import config
from pyre.api.v1.models import Order


ORDERS_KEY = "orders"

order = Typer(add_completion=False)


def _get_client() -> Client:
    return Client(base_url=f"{config.PYRE_ENDPOINT}/v1/orders")


@order.command()
def list() -> None:
    """List all market orders passed"""
    client = _get_client()
    response = client.get("/")
    orders = response.json()
    table = pd.DataFrame.from_records(orders)
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

    _datetime = pendulum.parse(datetime)
    order = Order(
        id=id,
        datetime=_datetime,
        ticker=ticker,
        quantity=quantity,
        price=price,
        fees=fees,
    )
    client.post("/", json=order.model_dump())
    

@order.command()
def bulk(
    file: str
) -> None:
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
def dump(output: Optional[str] = typer.Option(None, "-o", "--output", help="Output location to dump yaml")) -> None:
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
