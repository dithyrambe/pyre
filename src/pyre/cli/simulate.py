import pandas as pd
from typer import Typer
import typer

from pyre.cli.helpers import get_date_boundaries, plot, render_table
from pyre.constants import ORIGIN
from pyre.index import Index
from pyre.monte_carlo import MonteCarloSimulation
from pyre.strategy import MonthlyDCA


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
    simulations = monte_carlo.run(
        seed=seed, start_date=_start_date, end_date=_end_date, n=n_sim, progress=not quiet
    )
    quantiles = simulations.quantile([0.1, 0.5, 0.9], axis=1).T
    quantiles.columns = ["p10", "p50", "p90"]

    table = quantiles.map(lambda x: f"€{x:,.0f}").reset_index()
    table = table.groupby(pd.to_datetime(table["date"]).dt.year).last()
    table["date"] = table["date"].map(lambda x: f"{x}")

    if not quiet:
        if graph:
            plot(quantiles, colors=["red", "yellow", "green"])

        render_table(table, colors=[None, "red", "yellow", "green"])
    else:
        typer.echo(table.to_csv(sep="\t"))
