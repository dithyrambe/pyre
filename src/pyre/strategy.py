from pendulum import Date

def is_between(dt: Date, start_date: Date, end_date: Date) -> bool:
    return dt >= start_date and dt < end_date


class Strategy:
    def __init__(self, start_date: Date, end_date: Date) -> None:
        self.start_date = start_date
        self.end_date = end_date

    def execute(self, dt: Date, principal: float) -> float:
        raise NotImplementedError()


class NoOp(Strategy):
    def execute(self, dt: Date, principal: float) -> float:
        return principal


class MonthlyDCA(Strategy):
    def __init__(self, start_date: Date, end_date: Date, amount: float) -> None:
        super().__init__(start_date, end_date)
        self.amount = amount
        self.payments = []

    def execute(self, dt: Date, principal: float) -> float:
        if is_between(dt, self.start_date, self.end_date) and dt.is_same_day(dt.start_of("month")):
            self.payments.append({"dt": self.amount})
            return principal + self.amount
        return principal


class LumpSum(Strategy):
    ...
