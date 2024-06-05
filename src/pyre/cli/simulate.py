import numpy as np
import pandas as pd
from typer import Typer
import typer

from pyre.cli.helpers import get_date_boundaries, plot, render_table
from pyre.simulation.constants import ORIGIN
from pyre.simulation.index import Index
from pyre.simulation.monte_carlo import MonteCarloSimulation
from pyre.simulation.strategy import MonthlyDCA


app = Typer(add_completion=False)


@app.command()
def dca(
    symbol: str = typer.Option(..., help="Symbol of the considered market index"),
    amount: float = typer.Option(..., help="DCA monthly saving amount"),
    seed: float = typer.Option(0.0, help="Seed principal"),
    start_date: str = typer.Option(None, help="Date to start simulations"),
    end_date: str = typer.Option(None, help="Date to start simulations"),
    duration: int = typer.Option(10, help="Duration of the simulation in years (ignore if --end-date is passed)"),
    n_sim: int = typer.Option(100, "-n", "--n-sim", help="Number of simulations to draw"),
    graph: bool = typer.Option(False, help="Wether to plot graph"),
    quiet: bool = typer.Option(False, help="Plot raw text")
) -> None:
    _start_date, _end_date = get_date_boundaries(start_date, end_date, duration)

    idx = Index(symbol=symbol)
    idx.get_historical_data(start_date=ORIGIN)
    dca = MonthlyDCA(start_date=_start_date, end_date=_end_date, amount=amount)
    monte_carlo = MonteCarloSimulation(index=idx, strategy=dca)
    dates, principals = monte_carlo.run(
        seed=seed, start_date=_start_date, end_date=_end_date, n=n_sim, progress=not quiet
    )

    _quantiles = np.quantile(principals, q=[0.1, 0.5, 0.9], axis=1)
    quantiles = pd.DataFrame(_quantiles.T, columns=["p10", "p50", "p90"], index=pd.Index(dates, name="date"))
    quantiles = quantiles.join(dca.payments)
    quantiles["savings"] = quantiles["savings"].fillna(0).cumsum() + seed

    table = quantiles.map(lambda x: f"€{x:,.0f}").reset_index()
    table = table.groupby(pd.to_datetime(table["date"]).dt.year).last()
    table["date"] = table["date"].map(lambda x: f"{x}")

    if not quiet:
        if graph:
            plot(quantiles, colors=["red", "yellow", "green", None])

        render_table(table, colors=[None, "red", "yellow", "green", None])
    else:
        typer.echo(table.to_csv(sep="\t"))
