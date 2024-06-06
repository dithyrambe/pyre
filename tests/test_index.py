from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest

from pyre.simulation.constants import ORIGIN
from pyre.simulation.index import Index


@pytest.fixture()
def dummy_index_data():
    return pd.DataFrame(
        {"Close": [1.0, 3.0, 4.0]},
        index=pd.Index(pd.to_datetime(["2023-01-02", "2023-01-04", "2023-01-05"]))
    )


@patch("pyre.simulation.index.yf.Ticker.history")
def test_date_range_index(history: MagicMock, dummy_index_data: pd.DataFrame):
    history.return_value = dummy_index_data

    idx = Index("SYMBOL")
    idx.get_historical_data(start_date=ORIGIN)

    pd.testing.assert_index_equal(idx.data.index, pd.date_range("2023-01-02", "2023-01-05"))


@patch("pyre.simulation.index.yf.Ticker.history")
def test_interpolate(history: MagicMock, dummy_index_data: pd.DataFrame):
    history.return_value = dummy_index_data

    index = Index("SYMBOL")
    index.get_historical_data(start_date=ORIGIN)

    pd.testing.assert_series_equal
    pd.testing.assert_frame_equal(
        index.data,
        pd.DataFrame(
            {"Close": [1.0, 2.0, 3.0, 4.0]},
            index=pd.date_range("2023-01-02", "2023-01-05")
        )
    )


@patch("pyre.simulation.index.yf.Ticker.history")
def test_variations(history: MagicMock, dummy_index_data: pd.DataFrame):
    history.return_value = dummy_index_data

    idx = Index("SYMBOL")
    idx.get_historical_data(start_date=ORIGIN)
    pd.testing.assert_series_equal(
        idx.get_variations(),
        pd.Series([None, 1.0, 1.0/2, 1.0/3], index=idx.data.index, name="Close"),
    )


@patch("pyre.simulation.index.yf.Ticker.history")
def test_variation_mean(history: MagicMock, dummy_index_data: pd.DataFrame):
    history.return_value = dummy_index_data

    idx = Index("SYMBOL")
    idx.get_historical_data(start_date=ORIGIN)
    assert idx.get_variation_mean() == np.mean([1, 1/2, 1/3])


@patch("pyre.simulation.index.yf.Ticker.history")
def test_variation_std(history: MagicMock, dummy_index_data: pd.DataFrame):
    history.return_value = dummy_index_data

    idx = Index("SYMBOL")
    idx.get_historical_data(start_date=ORIGIN)
    np.testing.assert_almost_equal(idx.get_variation_std(), np.std([1, 1/2, 1/3], ddof=1))
