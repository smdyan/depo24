from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.bankDeposit.model.income import Income
from src.bankDeposit.service.utils import to_dec


class InterestTerms(IntEnum):
    END_OF_TERM = 1               # в конце срока (простые проценты, без капитализации)
    MONTHLY_COMPOUNDING = 2       # ежемесячно с капитализацией
    MONTHLY_PAYOUT = 3            # ежемесячно с выплатой (без капитализации)


def calc_income_array( 
    face_value: int | float,
    interest_rate: int | float,
    date_open: date,
    date_close: date,
    duration: int,
    interest_term: InterestTerms,
    day_count_base: int = 365,        
) -> list[Income]:

    if not face_value or not interest_rate or not duration:
        return []
    
    # Больше точности при промежуточных расчётах
    getcontext().prec = 28
    
    P = to_dec(face_value)
    r = to_dec(interest_rate) / Decimal(100)          # годовая ставка, доля
    days = Decimal(duration)
    D = Decimal(day_count_base)

    ret:list[Income] = []

    if interest_term == InterestTerms.END_OF_TERM:
        # Простые проценты без капитализации: P * r * t/365
        x = to_dec(P * r * (days / D))
        inc = Income(value=x, date_payment=date_close, period=int(days))
        ret.append(inc)

    if interest_term == InterestTerms.MONTHLY_COMPOUNDING:
        prev = date_open
        for next in _iter_months(date_open, date_close):
            delta = next - prev
            days = Decimal(delta.days)
            x = to_dec(P * r * (days / D))
            inc = Income(value=x, date_payment=next, period=int(days))
            ret.append(inc)
            prev = next
            P += x

    if interest_term == InterestTerms.MONTHLY_PAYOUT:
        prev = date_open
        for next in _iter_months(date_open, date_close):
            delta = next - prev
            days = Decimal(delta.days)
            x = to_dec(P * r * (days / D))
            inc = Income(value=x, date_payment=next, period=int(days))
            ret.append(inc)
            prev = next
    
    return ret


def _months_between(d1: date, d2: date) -> int:
    """Возвращает количество полных календарных месяцев между двумя датами"""
    if d1 > d2:
        d1, d2 = d2, d1
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def _iter_months(start: date, end: date):
    """генератор дат выплаты процентов 1 числа каждого месяца и заканчивая последним днем вклада"""
    n = date(start.year, start.month, 1)

    looping = True
    
    while looping:
        if(_months_between(end, n) == 0):
            n = end 
            looping = False
        else:
            n += relativedelta(months=1)
        
        yield n
