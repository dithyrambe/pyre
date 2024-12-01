from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


class SchemaValidationException(Exception): ...


@dataclass
class Column:
    name: str
    type: type[str] | type[float] | type[int]


@dataclass
class Schema:
    columns: list[Column]

    @property
    def colnames(self) -> list[str]:
        return [col.name for col in self.columns]

    @property
    def coltypes(self) -> list[type]:
        return [col.type for col in self.columns]

    def validate(self, df: pd.DataFrame) -> None:
        expected_types = {col.name: {col.type} for col in self.columns}
        actual_types = {col: set(df[col].apply(type).values) for col in df.columns}
        if actual_types != expected_types:
            raise SchemaValidationException(
                f"Dataframe doesn't comply with schema."
                f" Following columns have (some) wrong types: "
                f"{set(col for col, types in actual_types.items() if types != expected_types[col])}"
            )


TRANSACTION_SCHEMA = Schema(
    columns=[
        Column(name="event_date", type=str),
        Column(name="event_datetime", type=str),
        Column(name="description", type=str),
        Column(name="amount", type=float),
        Column(name="category", type=str),
        Column(name="subcategory", type=str),
    ]
)


class TransactionLoader(ABC):
    def __init__(
        self,
        sep: str = ";",
        decimal: str = ",",
        encoding: str = "latin",
        strict: bool = True,
    ):
        self.sep = sep
        self.decimal = decimal
        self.encoding = encoding
        self.strict = strict

    def read(self, path: str | Path) -> pd.DataFrame:
        raw = self.read_raw(path=path)
        df = pd.DataFrame().assign(
            event_date=self.get_event_date(raw),
            event_datetime=self.get_event_datetime(raw),
            description=self.get_description(raw),
            amount=self.get_amount(raw),
            category=self.get_category(raw),
            subcategory=self.get_subcategory(raw),
        )
        if self.strict:
            TRANSACTION_SCHEMA.validate(df)
        return df

    @abstractmethod
    def read_raw(self, path: str | Path) -> pd.DataFrame: ...

    @abstractmethod
    def get_event_date(self, df: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def get_event_datetime(self, df: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def get_description(self, df: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def get_amount(self, df: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def get_category(self, df: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def get_subcategory(self, df: pd.DataFrame) -> pd.Series: ...
