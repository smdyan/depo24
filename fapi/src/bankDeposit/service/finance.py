from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.bankDeposit.model.income import Income

def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)


def months_between(d1: date, d2: date) -> int:
    """Возвращает количество полных календарных месяцев между двумя датами."""
    # гарантируем, что d1 <= d2
    if d1 > d2:
        d1, d2 = d2, d1
    
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def iter_months(start: date, end: date):

    n = date(start.year, start.month, 1)

    looping = True
    
    while looping:
        if(months_between(end, n) == 0):
            n = end 
            looping = False
        else:
            n += relativedelta(months=1)
        
        yield n


def calc_total_income(
        obj
) -> int:
    sum = 0
    for income in obj.incomes:
        sum += income.value
    return sum


def calc_gross_value(obj) -> int:
    return obj.face_value + obj.income_value


def calc_effective_int_rate(obj) -> int:
    n= obj.income_value/obj.face_value*(365/obj.duration)*100
    return int(n)


# Больше точности при промежуточных расчётах
getcontext().prec = 28

class InterestTerms(IntEnum):
    END_OF_TERM = 1               # в конце срока (простые проценты, без капитализации)
    MONTHLY_COMPOUNDING = 2       # ежемесячно с капитализацией
    MONTHLY_PAYOUT = 3            # ежемесячно с выплатой (без капитализации)

def _to_dec(x) -> Decimal:
    return Decimal(str(x))


def calc_income_array( 
    face_value: int | float,
    interest_rate: int | float,
    date_open: date,
    date_close: date,
    duration: int,
    interest_term: InterestTerms,
    day_count_base: int = 365,        
) -> list[int]:

    if not face_value or not interest_rate or not duration:
        return 0
    
    P = _to_dec(face_value)
    r = _to_dec(interest_rate) / Decimal(100)          # годовая ставка, доля
    days = Decimal(duration)
    D = Decimal(day_count_base)

    ret:list[Income] = []

    if interest_term == InterestTerms.END_OF_TERM:
        # Простые проценты без капитализации: P * r * t/365
        x1 = P * r * (days / D)
        x2 = int(x1.to_integral_value(rounding=ROUND_FLOOR))
        inc = Income(value=x2, date_payment=date_close)
        ret.append(inc)

    if interest_term == InterestTerms.MONTHLY_COMPOUNDING:
        prev = date_open
        i=0
        for next in iter_months(date_open, date_close):
            delta = next - prev
            days = Decimal(delta.days)
            x1 = P * r * (days / D)
            x2 = int(x1.to_integral_value(rounding=ROUND_FLOOR))
            inc = Income(value=x2, date_payment=next)
            ret.append(inc)
            prev = next
            P += x2
            i+=1
            print("777iteration: ", i)

    print(ret)
    return ret




