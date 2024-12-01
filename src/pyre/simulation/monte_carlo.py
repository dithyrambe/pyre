from pendulum import Date
from rich.progress import track
import numpy as np
import pandas as pd

from pyre.simulation.index import Index
from pyre.simulation.strategy import Strategy


class MonteCarloSimulation:
    def __init__(self, index: Index, strategy: Strategy) -> None:
        self.index = index
        self.strategy = strategy

    def run(
        self, seed: float, start_date: Date, end_date: Date, n: int = 1, progress: bool = False
    ):
        date_range = (end_date.subtract(days=1) - start_date).range("days")
        dates = [*date_range]

        mean = self.index.get_variation_mean()
        std = self.index.get_variation_std()
        variations = np.random.normal(loc=mean, scale=std, size=(len(dates), n))
        return dates, self.simulate(
            seed=seed, dates=dates, variations=variations, progress=progress
        )

    def simulate(
        self, seed: float, dates: list[Date], variations: np.ndarray, progress: bool = False
    ) -> pd.DataFrame:
        principals = seed * np.ones(variations.shape[1])
        _principals = np.ones_like(variations)
        iterator = enumerate(zip(dates, variations))
        if progress:
            iterator = track(iterator, total=len(dates), description="Simulating")

        for i, (date, variation) in iterator:
            new_principals = self.strategy.execute(date=date, principal=principals)
            new_principals *= 1 + variation
            _principals[i] *= new_principals
            principals = new_principals

        return np.row_stack(_principals)
