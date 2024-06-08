from typing import Optional
from sqlalchemy import select

import pandas as pd
import pendulum
import typer
import yaml
from sqlalchemy.orm import Session
from typer import Typer

from pyre.cli.helpers import render_table
from pyre.db.engine import create_engine


ORDERS_KEY = "orders"

order = Typer(add_completion=False)

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
    engine = create_engine()
    with Session(engine) as session:
        order = Order(
            id=id,
            datetime=pendulum.parse(datetime),
            ticker=ticker,
            quantity=quantity,
            price=price,
            fees=fees,
        )
        session.add(order)
        session.commit()


@order.command()
def bulk(
    file: str
) -> None:
    """Insert stock market orders in bulk from yaml"""
    with open(file) as f:
        data = yaml.safe_load(f)
        orders = [
            Order(
                id=int(record["id"]),
                datetime=pendulum.parse(record["datetime"]),
                ticker=str(record["ticker"]),
                quantity=int(record["quantity"]),
                price=float(record["price"]),
                fees=float(record["fees"]),
            )
            for record in data[ORDERS_KEY]
        ]

    engine = create_engine()
    with Session(engine) as session:
        for order in orders:
            session.query(Order).filter(
                Order.id == order.id
            ).delete()
            session.add(order)
        session.commit()


@order.command()
def list() -> None:
    """List all market orders passed"""
    engine = create_engine()
    with Session(engine) as session:
        stmt = select(Order)
        results = session.execute(stmt)
        fields = ["id", "datetime", "ticker", "quantity", "price", "fees"]
        table = pd.DataFrame(
            data=[
                {
                    field: str(getattr(r, field))
                    for field in fields
                } 
                for r, in results
            ],
            columns=fields
        )
        render_table(table)


@order.command()
def dump(output: Optional[str] = typer.Option(None, "-o", "--output", help="Output location to dump yaml")) -> None:
    """Dump all orders (for backup purposes)"""
    engine = create_engine()
    with Session(engine) as session:
        stmt = select(Order)
        results = session.execute(stmt)
        orders = {
            "orders": [
                {
                    "id": order.id,
                    "datetime": pendulum.parse(f"{order.datetime}").to_iso8601_string(),
                    "ticker": order.ticker,
                    "quantity": order.quantity,
                    "price": order.price,
                    "fees": order.fees
                }
                for order, in results
            ]
        }
        if output:
            with open(output, "w") as f:
                yaml.safe_dump(f)
        else:
            typer.echo(yaml.safe_dump(orders))


@order.command()
def delete(id: int) -> None:
    """Delete an order by its ID"""
    engine = create_engine()
    with Session(engine) as session:
        session.query(Order).filter(
            Order.id == id
        ).delete()
        session.commit()

