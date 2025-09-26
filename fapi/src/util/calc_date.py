from datetime import date, timedelta

def add_days(d: date, days: int) -> date:
    return d + timedelta(days=days)