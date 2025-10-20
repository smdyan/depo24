from datetime import date, timedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext


def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)

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

def calc_income_value(
    face_value: int | float,
    interest_rate: int | float,
    duration: int,
    interest_term: InterestTerms,
    day_count_base: int = 365,
) -> int:
    
    if not face_value or not interest_rate or not duration:
        return 0
    
    P = _to_dec(face_value)
    r = _to_dec(interest_rate) / Decimal(100)          # годовая ставка, доля
    days = Decimal(duration)
    D = Decimal(day_count_base)

    if interest_term == InterestTerms.END_OF_TERM:
        # Простые проценты без капитализации: P * r * t/365
        inc = P * r * (days / D)

    elif interest_term == InterestTerms.MONTHLY_PAYOUT:
        # Ежемесячно выплата процентов (без капитализации):
        months = (days // Decimal(30))            # целые месяцы, приближенно
        rem_days = days - months * Decimal(30)    # остаток дней
        inc = P * (r / Decimal(12)) * months + P * r * (rem_days / D)

    elif interest_term == InterestTerms.MONTHLY_COMPOUNDING:
        # Ежемесячная капитализация:
        # Эффективный множитель ≈ (1 + r/12)^{months} * (1 + r/365)^{rem_days}
        # Доход = P * (factor - 1)
        months = (days // Decimal(30))
        rem_days = days - months * Decimal(30)
        month_rate = r / Decimal(12)
        day_rate = r / D

        factor_months = (Decimal(1) + month_rate) ** months
        factor_days = (Decimal(1) + day_rate) ** rem_days
        factor = factor_months * factor_days
        inc = P * (factor - Decimal(1))

    else:
        # неизвестный режим — безопасно вернуть 0
        inc = Decimal(0)

    # Округление вниз до целого (как int в БД):
    return int(inc.to_integral_value(rounding=ROUND_FLOOR))

