from datetime import date, timedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext


# Больше точности при промежуточных расчётах
getcontext().prec = 28

class InterestTerms(IntEnum):
    END_OF_TERM = 1               # в конце срока (простые проценты, без капитализации)
    MONTHLY_COMPOUNDING = 2       # ежемесячно с капитализацией
    MONTHLY_PAYOUT = 3            # ежемесячно с выплатой (без капитализации)

def _to_dec(x) -> Decimal:
    return Decimal(str(x))

def calc_income(incomes) -> int:
    ret = 0
    for income in incomes:
        ret += income.value
    return int(ret)

