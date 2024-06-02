from pathlib import Path
import pytest

import pandas as pd
from pyre.index import Index


@pytest.fixture()
def urth():
    path = Path(__file__).parent / "resources" / "URTH.csv"
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["Date"])
    data = data.set_index("date").drop("Date", axis="columns")

    idx = Index(symbol="URTH")
    idx.data = data
    return idx
    
