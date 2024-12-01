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
ANNUALIZED_RETURN = 0.075
INTERVAL = END - START

pea = PEA(fees=0.00, annualized_return=ANNUALIZED_RETURN, opening_date=START)  # type: ignore
cto = CTO(fees=0.00, annualized_return=ANNUALIZED_RETURN, opening_date=START)  # type: ignore
av = AV(fees=0.010, annualized_return=ANNUALIZED_RETURN, opening_date=START)  # type: ignore

data = {
    _: []
    for _ in [
        "date",
        "pea",
        "cto",
        "av",
    ]
}

for dt in INTERVAL.range("months"):
    contribution = Contribution(amount=AMOUNT, datetime=dt)
    withdrawal = Withdrawal(pct=PCT, datetime=dt)

    if pea.total_contribution(dt) + contribution.amount < pea.CONTRIBUTION_LIMIT:
        pea.contribute(contribution=contribution)
    else:
        cto.contribute(contribution=contribution)
        av.contribute(contribution=contribution)

    pea_net, pea_tax = pea.withdraw(withdrawal=withdrawal)
    cto_net, cto_tax = cto.withdraw(withdrawal=withdrawal)
    av_net, av_tax = av.withdraw(withdrawal=withdrawal)
    data["date"].append(dt)
    data["pea"].append(pea_net)
    data["cto"].append(cto_net)
    data["av"].append(av_net)

df = pd.DataFrame(data).set_index("date")
df["Rente pea+cto"] = df["pea"] + df["cto"]
df["Rente pea+av"] = df["pea"] + df["av"]
(df[["Rente pea+cto", "Rente pea+av"]]).plot.line(
    figsize=(15, 10), legend=True, title=f"DCA €{AMOUNT} / month for {INTERVAL.in_years()} years"
)
plt.show()
plt.savefig("/tmp/fig.png", format="png")
