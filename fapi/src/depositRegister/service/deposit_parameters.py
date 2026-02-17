from datetime import date, timedelta


def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)
