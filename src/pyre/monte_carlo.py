from rich.progress import track
from pendulum import Date
import numpy as np
import pandas as pd

from pyre.index import Index
from pyre.strategy import Strategy


class MonteCarloSimulation:
    def __init__(self, index: Index, strategy: Strategy) -> None:
        self.index = index
        self.strategy = strategy

    def run(self, seed: float, start_date: Date, end_date: Date, n: int = 1, progress: bool = False):
        date_range = (end_date.subtract(days=1) - start_date).range("days")
        dates = [*date_range]
        _range = range(n)
        if progress:
            _range = track(_range, total=n, description="Simulating...")
        simulations = [pd.Series(self.simulate(seed=seed, dates=dates), index=dates) for _ in _range]
        return pd.concat(simulations, axis=1)


    def simulate(self, seed: float, dates: list[Date]) -> pd.Series:
        principals = [seed]
        mean = self.index.get_variation_mean()
        std = self.index.get_variation_std()

        variations = np.random.normal(loc=mean, scale=std, size=len(dates))
        for date, variation in zip(dates, variations):
            new_principal = self.strategy.execute(dt=date, principal=principals[-1])
            new_principal *= 1 + variation
            principals.append(new_principal)

        return pd.Series(principals[1:], index=dates)
