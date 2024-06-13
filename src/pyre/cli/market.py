from enum import Enum
from typing import List, Optional
import time

import pandas as pd
import psycopg2
import typer
import yfinance
from sqlalchemy.orm import Session
from typer import Typer

from pyre.config import config
from pyre.db.engine import create_engine
from pyre.db.schemas import Order, StockData
from pyre.exceptions import PyreException


NULL = psycopg2.extensions.AsIs('NULL')

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
        [[*set(COLUMN_MAPPING.values())]]
    )
    return df


def _dump_records(db: Session, records: pd.DataFrame):
    min_max_dates = records["datetime"].agg(("min", "max"))
    db.query(StockData).filter(
        StockData.datetime >= min_max_dates["min"],
        StockData.datetime <= min_max_dates["max"],
    ).delete()
    db.commit()

    records = records.fillna(NULL)
    db.bulk_save_objects([StockData(**record) for record in records.to_dict(orient="records")])
    db.commit()


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


@market.command()
def refresh(
    forever: bool = typer.Option(False, help="Whether to crawl forever"), 
    polling_interval: int = typer.Option(config.PYRE_POLLING_INTERVAL, help="Time interval to fetch data again")
):
    """Crawl latest market data"""
    engine = create_engine()

    while True:
        with Session(engine) as db:
            if db.query(Order).first() is not None:
                results = db.query(Order).all()
                tickers, dts = zip(*[(order.ticker, order.datetime) for order in results])
                min_datetime = min(dts).date()
                records = _download(
                    tickers=[*set(tickers)],
                    start_datetime=f"{min_datetime}",
                    interval="1d",
                )
                _dump_records(db, records)
        if not forever:
            break
        time.sleep(polling_interval or config.PYRE_POLLING_INTERVAL)
