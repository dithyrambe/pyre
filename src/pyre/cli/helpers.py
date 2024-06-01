from typing import Optional, Tuple
from pendulum import Date
import pendulum


def get_date_boundaries(
    start_date: str, end_date: Optional[str] = None, duration: Optional[int] = None
) -> Tuple[Date, Date]:
    _start_date = pendulum.parse(start_date).date()
    
    if end_date is not None:
        _end_date = pendulum.parse(end_date).date()
        return _start_date, _end_date

    if end_date is None and duration is not None:
        return _start_date, _start_date.add(years=duration)

    raise ValueError("Must specified either end_date or duration")
