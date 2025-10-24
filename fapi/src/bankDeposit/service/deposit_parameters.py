from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from enum import IntEnum
from decimal import Decimal, ROUND_FLOOR, getcontext, ROUND_HALF_UP, InvalidOperation
from src.bankDeposit.model.income import Income
from src.bankDeposit.service.utils import to_dec


def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)


def calc_total_income(obj) -> Decimal:
    sum = 0
    for income in obj.incomes:
        i = to_dec(income.value)
        sum += i
    return sum


def calc_gross_value(obj) -> Decimal:
    i = to_dec(obj.income_value)
    f = to_dec(obj.face_value)
    ret = f+i
    return ret #при сложении мантисса не увеличится


def calc_effective_int_rate(obj) -> Decimal:
    i = to_dec(obj.income_value)
    f = to_dec(obj.face_value)
    days = Decimal(obj.duration)
    n= i/f*(365/days)*100
    return to_dec(n)


