from datetime import date


def iso_week_begin(d: date) -> date:
    iso = d.isocalendar()
    return date.fromisocalendar(iso[0], iso[1], 1)
