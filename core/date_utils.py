from datetime import date
from typing import Tuple


def this_week() -> Tuple[int, int]:
    week_begin = iso_week_begin(date.today())
    (year, week, _) = week_begin.isocalendar()
    return (year, week)


def iso_week_begin(d: date) -> date:
    iso = d.isocalendar()
    return date.fromisocalendar(iso[0], iso[1], 1)
