# type: ignore
import matplotlib.pyplot as plt
import pandas as pd
import pendulum
from pyre.tax_wrappers.av import AV
from pyre.tax_wrappers.base import Contribution, Withdrawal
from pyre.tax_wrappers.cto import CTO
from pyre.tax_wrappers.pea import PEA

plt.style.use("ggplot")


INVESTMENT_DURATION = pendulum.Duration(years=20)
AMOUNT = 3000.0
PCT = 0.035
START = pendulum.parse("2024-11-01")
END = START + INVESTMENT_DURATION
DEATH = pendulum.parse("1991-08-27").add(years=100)
ANNUALIZED_RETURN = 0.07
INTERVAL = END - START
INFLATION = 0.03
MONTHLY_INFLATION = (1 + INFLATION) ** (1 / 12) - 1


def get_inflation(dt):
    months = pendulum.Interval(start=START, end=dt).in_months()
    return (1 + MONTHLY_INFLATION) ** months


pea = PEA(fees=0.00, annualized_return=ANNUALIZED_RETURN, opening_date=pendulum.parse("2024-05-01"))  # type: ignore
cto = CTO(fees=0.00, annualized_return=ANNUALIZED_RETURN, opening_date=START)  # type: ignore
av = AV(fees=0.010, annualized_return=ANNUALIZED_RETURN, opening_date=pendulum.parse("2025-05-01"))  # type: ignore

pea.contribute(Contribution(amount=65000, datetime=pendulum.parse("2024-10-01")))

data = {
    _: []
    for _ in [
        "date",
        "pea",
        "av",
        "cto",
    ]
}

for dt in (DEATH - START).range("months"):
    contribution = Contribution(amount=AMOUNT, datetime=dt)
    withdrawal = Withdrawal(pct=PCT, datetime=dt)

    if dt <= END:
        if pea.total_contribution(dt) + contribution.amount < pea.CONTRIBUTION_LIMIT:
            pea.contribute(contribution=contribution)
        elif av.total_contribution(dt) + contribution.amount < av.SOFT_CONTRIBUTION_LIMIT:
            av.contribute(contribution=contribution)
        else:
            cto.contribute(contribution=contribution)

    pea_net, pea_tax = pea.withdraw(withdrawal=withdrawal)
    cto_net, cto_tax = cto.withdraw(withdrawal=withdrawal)
    av_net, av_tax = av.withdraw(withdrawal=withdrawal)
    data["date"].append(dt)
    data["pea"].append(pea_net)
    data["av"].append(av_net)
    data["cto"].append(cto_net)

df = pd.DataFrame(data).set_index("date")
inflations = pd.Series([get_inflation(_) for _ in df.index], index=df.index)
(df.divide(inflations, axis=0)).plot.area(
    figsize=(15, 10),
    legend=True,
    stacked=True,
    title=f"DCA €{AMOUNT} / month for {INTERVAL.in_years()} years",
    grid=True,
    alpha=0.5,
)
plt.show()
plt.savefig("/tmp/fig.png", format="png")
