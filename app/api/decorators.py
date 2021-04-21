from functools import wraps
from .errors import ValidationError
from core.date_utils import is_valid_iso_week


def validate_week(f):
    @wraps(f)
    def with_validation(*args, **kwargs):
        year = kwargs.get("year")
        week = kwargs.get("week")
        if (year or week) and not is_valid_iso_week(year, week):
            raise ValidationError("invalid ISO week date")
        return f(*args, **kwargs)

    return with_validation