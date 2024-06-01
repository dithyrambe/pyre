from itertools import cycle
from typing import List, Optional, Tuple
from pendulum import Date
from rich.console import Console
from rich.table import Table
import pandas as pd
import pendulum
import plotille


def get_date_boundaries(
    start_date: str, end_date: Optional[str] = None, duration: Optional[int] = None
) -> Tuple[Date, Date]:
    _start_date = pendulum.parse(start_date).date()
    
    if end_date is not None:
        _end_date = pendulum.parse(end_date).date()
        return _start_date, _end_date

    if end_date is None and duration is not None:
        return _start_date, _start_date.add(years=duration)

    raise ValueError("Must specified either end_date or duration")


def plot(df: pd.DataFrame, colors: Optional[List[str]] = None) -> None:
    _colors = iter(colors) if colors is not None else cycle(["red", "yellow", "green", "blue"])

    fig = plotille.Figure()
    fig.width = 120
    for col in df.columns:
        fig.plot(df.index, df[col], lc=next(_colors), label=col)
    fig.x_label = df.index.name
    fig.y_label = "€"
    print(fig.show(legend=True))


def render_table(df: pd.DataFrame, title: Optional[str] = None, colors: Optional[List[str]] = None) -> None:
    _colors = iter(colors) if colors is not None else cycle(["red", "yellow", "green", "blue"])

    table = Table(title=title)

    for col in df.columns:
        table.add_column(col, justify="right", style=next(_colors))

    for row in df.values:
        table.add_row(*row)

    console = Console()
    console.print(table)
