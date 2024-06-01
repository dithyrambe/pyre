from typing import Union

from pendulum import Date
import numpy as np
import pandas as pd


def is_between(dt: Date, start_date: Date, end_date: Date) -> bool:
    return dt >= start_date and dt < end_date


class Strategy:
    def __init__(self, start_date: Date, end_date: Date) -> None:
        self.start_date = start_date
        self.end_date = end_date

    def execute(self, dt: Date, principal: float) -> float:
        raise NotImplementedError()


class NoOp(Strategy):
    def execute(self, dt: Date, principal: float) -> float:
        return principal


class MonthlyDCA(Strategy):
    def __init__(self, start_date: Date, end_date: Date, amount: float) -> None:
        super().__init__(start_date, end_date)
        self.amount = amount
        self._payments = []

    def execute(self, dt: Date, principal: Union[float, np.ndarray]) -> float:
        if is_between(dt, self.start_date, self.end_date) and dt.is_same_day(dt.start_of("month")):
            self._payments.append({"date": dt, "savings": self.amount})
            return principal + self.amount
        return principal
    
    @property
    def payments(self) -> pd.Series:
        return pd.DataFrame.from_records(self._payments).set_index("date")["savings"]


class LumpSum(Strategy):
    ...
