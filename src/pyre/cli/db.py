from enum import Enum
from typing import List, Optional
from sqlalchemy import select
import time

import pandas as pd
import pendulum
import psycopg2
import typer
import yaml
import yfinance
from pyre.cli.helpers import render_table
from sqlalchemy.orm import Session
from typer import Typer

from pyre.config import config
from pyre.db.engine import create_engine
from pyre.db.schemas import Investment, StockData
from pyre.exceptions import PyreException

class TimePeriod(str, Enum):
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YEAR_TO_DATE = "ytd"
    MAX = "max"


class TimeInterval(str, Enum):
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


COLUMN_MAPPING = {
    "Date": "datetime",
    "Datetime": "datetime",
    "Ticker": "ticker",
    "Open": "open",
    "Close": "close",
    "High": "high",
    "Low": "low",
    "Volume": "volume",
}

market = Typer(add_completion=False)
order = Typer(add_completion=False)

def _download(
    tickers: List[str],
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    period: str = "max", 
    interval: str = "1d"
    ) -> pd.DataFrame:
    data = yfinance.download(
        tickers=" ".join(tickers),
        start=start_datetime,
        end=end_datetime,
        period=period,
        interval=interval,
        ignore_tz=True,
    )
    df = (
        data
        .stack("Ticker", future_stack=True)
        .reset_index()
        .rename(columns=COLUMN_MAPPING)
        .fillna(psycopg2.extensions.AsIs('NULL'))
        [[*set(COLUMN_MAPPING.values())]]
    )
    return df.to_dict(orient="records")


def _dump_records(session, records):
    for record in records:
        stock_data = StockData(**record)
        session.query(StockData).filter(
            StockData.ticker == stock_data.ticker,
            StockData.datetime == stock_data.datetime
        ).delete()
        session.add(stock_data)
    session.commit()


@market.command()
def fetch(
    ticker: str,
    start_datetime: Optional[str] = typer.Option(None, help="Start datetime to fetch data from (inclusive)"),
    end_datetime: Optional[str] = typer.Option(None, help="Start datetime to fetch data to (exclusive)"),
    period: TimePeriod = typer.Option("1mo", help="Period of time to fetch data"),
    interval: TimeInterval = typer.Option("1d", help="Time interval"),
) -> None:
    """Fetches data for ticker from yahoo finance and store them in DB"""
    if not period and (not start_datetime and not end_datetime):
        raise PyreException("Must specify period or couple (start_datetime, end_datetime)")

    if start_datetime or end_datetime:
        period = TimePeriod("max")

    tickers = ticker.split(",")
    records = _download(tickers, start_datetime, end_datetime, period.value, interval.value)

    engine = create_engine()
    with Session(engine) as session:
        _dump_records(session, records)


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
        investment = Investment(
            id=id,
            datetime=pendulum.parse(datetime),
            ticker=ticker,
            quantity=quantity,
            price=price,
            fees=fees,
        )
        session.add(investment)
        session.commit()


@order.command()
def bulk(
    file: str
) -> None:
    """Insert stock market orders in bulk from yaml"""
    with open(file) as f:
        data = yaml.safe_load(f)
        investments = [
            Investment(
                id=int(record["id"]),
                datetime=pendulum.parse(record["datetime"]),
                ticker=str(record["ticker"]),
                quantity=int(record["quantity"]),
                price=float(record["price"]),
                fees=float(record["fees"]),
            )
            for record in data["investments"]
        ]

    engine = create_engine()
    with Session(engine) as session:
        for investment in investments:
            session.query(Investment).filter(
                Investment.id == investment.id
            ).delete()
            session.add(investment)
        session.commit()


@order.command()
def list() -> None:
    """List all market orders passed"""
    engine = create_engine()
    with Session(engine) as session:
        stmt = select(Investment)
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
def delete(id: int) -> None:
    """Delete an order by its ID"""
    engine = create_engine()
    with Session(engine) as session:
        session.query(Investment).filter(
            Investment.id == id
        ).delete()
        session.commit()


@market.command()
def refresh(setup: bool = False, forever: bool = False):
    if setup:
        bulk(config.PYRE_INVESTMENTS_FILE)
        
    engine = create_engine()
    with Session(engine) as session:
        stmt = select(Investment)
        results = session.execute(stmt)
        tickers, dts = zip(*[(investment.ticker, investment.datetime) for investment, in results])

    engine = create_engine()
    min_datetime = min(dts).date()

    records = _download(
        tickers=[*set(tickers)],
        start_datetime=f"{min_datetime}",
        interval="1d",
    )

    with Session(engine) as session:
        _dump_records(session, records)

    while forever:
        time.sleep(config.PYRE_POLLING_INTERVAL)
        records = _download(
            tickers=[*set(tickers)],
            start_datetime=f"{min_datetime}",
            interval="1d",
        )

        with Session(engine) as session:
            _dump_records(session, records)

