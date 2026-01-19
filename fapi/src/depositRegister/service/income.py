from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.depositRegister.model.income import Income
from src.depositRegister.model.parameters import InterestTerms, PeriodAnchor
from src.depositRegister.model.income import IncomeStatus
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.service.utils import to_dec


def calc_income_array(
    deposit: Deposit,
    day_count_base: int = 365,        
) -> list[Income]:
    
    # Больше точности при промежуточных расчётах
    getcontext().prec = 28
    
    date_open = deposit.date_open
    date_close = deposit.date_close
    interest_term = deposit.interest_term
    interest_basis = deposit.interest_period_basis                 # to delete - not used
    
    P = to_dec(deposit.principal_value)
    r = to_dec(deposit.nominal_rate) / Decimal(100)
    days = Decimal(deposit.duration)
    D = Decimal(day_count_base)

    ret:list[Income] = []

    if not deposit.principal_value or not deposit.nominal_rate or not deposit.duration:
        return []

    if interest_term == InterestTerms.END_OF_TERM:
        x = to_dec(P * r * (days / D))
        inc = Income(value=x, date_payment=date_close, period=int(days), status=IncomeStatus.PENDING)
        ret.append(inc)

    if interest_term == InterestTerms.MONTHLY_COMPOUND:
        prev = date_open
        for next in _iter_months(date_open, date_close):
            delta = next - prev
            days = Decimal(delta.days)
            x = to_dec(P * r * (days / D))
            inc = Income(value=x, date_payment=next, period=int(days), status=IncomeStatus.PENDING)
            ret.append(inc)
            prev = next
            P += x

    if interest_term == InterestTerms.MONTHLY_PAYOUT:
        prev = date_open
        for next in _iter_months(date_open, date_close):
            delta = next - prev
            days = Decimal(delta.days)
            x = to_dec(P * r * (days / D))
            inc = Income(value=x, date_payment=next, period=int(days), status=IncomeStatus.PENDING)
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
