import pendulum
import pytest

from pyre.simulation.strategy import MonthlyDCA


@pytest.mark.parametrize(
    argnames=("date", "expected"),
    argvalues=[
        (pendulum.parse("2022-01-01").date(), 10_000),
        (pendulum.parse("2022-02-01").date(), 11_000),
        (pendulum.parse("2022-03-01").date(), 11_000),
        (pendulum.parse("2022-04-13").date(), 10_000),
        (pendulum.parse("2022-06-01").date(), 10_000),
    ],
)
def test_dca(date, expected):
    start_date = pendulum.parse("2022-02-01").date()
    end_date = pendulum.parse("2022-06-01").date()

    principal = 10_000

    dca = MonthlyDCA(start_date=start_date, end_date=end_date, amount=1000)
    new_principal = dca.execute(date=date, principal=principal)
    assert new_principal == expected
