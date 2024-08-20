from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Column:
    name: str
    type: type[str] | type[float] | type[int]


@dataclass
class Schema:
    columns: list[Column]


SCHEMA = Schema(
    [
        Column(name="event_date", type=str),
        Column(name="event_datetime", type=str),
        Column(name="description", type=str),
        Column(name="amount", type=float),
        Column(name="category", type=str),
        Column(name="subcategory", type=str),
    ]
)


class TransactionLoader(ABC):
    SEP = ","
    DECIMAL = "."
    ENCODING = "utf-8"

    def read(self, path: str | Path) -> pd.DataFrame:
        raw = self.read_raw(path=path)
        df = (
            pd.DataFrame()
            .assign(
                event_date=self.get_event_date(raw),
                event_datetime=self.get_event_datetime(raw),
                description=self.get_description(raw),
                amount=self.get_amount(raw),
                category=self.get_category(raw),
                subcategory=self.get_subcategory(raw),
            )
        )
        return df
        
    @abstractmethod
    def read_raw(self, path: str | Path) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_event_date(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abstractmethod
    def get_event_datetime(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abstractmethod
    def get_description(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abstractmethod
    def get_amount(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abstractmethod
    def get_category(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abstractmethod
    def get_subcategory(self, df: pd.DataFrame) -> pd.Series:
        ...
