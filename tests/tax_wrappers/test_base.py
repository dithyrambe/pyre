import pendulum
from pyre.tax_wrappers.base import Contribution, TaxWrapper, Withdrawal


class DummyTaxWrapper(TaxWrapper):
    def withdraw(self, withdrawal: Withdrawal) -> tuple[float, float]:
        return super().withdraw(withdrawal)


def test_withdrawal_persistence():
    contributions = [
        Contribution(1000, datetime=pendulum.parse("2024-01-01")),
        Contribution(1000, datetime=pendulum.parse("2024-02-01")),
    ]
    withdrawal = Withdrawal(datetime=pendulum.parse("2024-03-01"), amount=1000)
    tw = DummyTaxWrapper(annualized_return=0.1)
    for contribution in contributions:
        tw.contribute(contribution)
    tw.withdraw(withdrawal)

    rate = 1 + tw.monthly_return

    assert tw.portfolio_value(pendulum.parse("2023-12-01")) == 0
    assert tw.portfolio_value(pendulum.parse("2024-01-01")) == 1000
    assert tw.portfolio_value(pendulum.parse("2024-02-01")) == 1000 * rate + 1000
    assert tw.portfolio_value(pendulum.parse("2024-03-01")) == 1000 * rate**2 + 1000 * rate - 1000
    assert (
        tw.portfolio_value(pendulum.parse("2024-04-01"))
        == (1000 * rate**2 + 1000 * rate - 1000) * rate
    )
