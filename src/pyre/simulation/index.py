from typing import Optional
from pendulum import Date
import pandas as pd
import yfinance as yf

CLOSING_COL = "Close"


class Index:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.ticker = yf.Ticker(self.symbol)
        self.data = pd.DataFrame(columns=[CLOSING_COL])

    def get_historical_data(
        self, start_date: Date, end_date: Optional[Date] = None
    ) -> pd.DataFrame:
        start = start_date.to_date_string()
        end = end_date.to_date_string() if end_date is not None else end_date
        data = self.ticker.history(start=start, end=end)

        min_available = data.index.min()
        max_available = data.index.max()
        self.data = data.reindex(pd.date_range(min_available, max_available)).interpolate(
            method="linear"
        )

    def get_variations(self) -> pd.Series:
        return self.data[CLOSING_COL].pct_change(fill_method=None)

    def get_variation_mean(self) -> float:
        return float(self.get_variations().mean())

    def get_variation_std(self) -> float:
        return float(self.get_variations().std())
