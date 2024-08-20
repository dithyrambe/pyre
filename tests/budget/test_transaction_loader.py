from pathlib import Path

import pytest

from pyre.budget.transaction_loader.banque_populaire import BanquePopulaireLoader



@pytest.mark.parametrize(
    argnames=("loader", "path"),
    argvalues=[
        (BanquePopulaireLoader(), "banque_populaire.csv"),
    ]
)
def test_banque_populaire_loader(loader, path):
    path = Path(__file__).parent / "data" / "transactions" / path
    df = loader.read(path)
    assert not df.empty
