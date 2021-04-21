from datetime import date
from typing import Tuple


def is_valid_iso_week(year: int, week: int) -> bool:
    (max_year, max_week) = this_week()
    if week < 1 or week > 52 or year > max_year:
        return False
    return year < max_year or week <= max_week


def this_week() -> Tuple[int, int]:
    week_begin = iso_week_begin(date.today())
    (year, week, _) = week_begin.isocalendar()
    return (year, week)


def iso_week_begin(d: date) -> date:
    iso = d.isocalendar()
    return date.fromisocalendar(iso[0], iso[1], 1)
