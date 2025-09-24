from datetime import date, timedelta

def calcDepositCloseDate(d: date, days: int) -> date:
    return d + timedelta(days=days)