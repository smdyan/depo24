from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_FLOOR, getcontext, ROUND_HALF_UP, InvalidOperation
from src.bankDeposit.model.income import Income, IncomeStatus
from src.bankDeposit.model.parameters import InterestTerms
from src.bankDeposit.service.utils import to_dec


def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)

def _calc_begin_date(date_payment: date, duration: int) -> date:
    return date_payment - timedelta(days=duration)


def calc_interest_accrued(obj) -> Decimal:
    sum = 0
    today = date.today()
    for income in obj.incomes:
        date_begin = _calc_begin_date(income.date_payment, income.period)
        date_end = income.date_payment
        
        if(income.status == IncomeStatus.PENDING and today > date_end):
            sum += income.value

        elif(income.status == IncomeStatus.PENDING and today <= date_end):
            days = (today - date_begin).days
            sum = income.value*days/income.period

    return to_dec(sum)
    

def calc_interest_paid(obj) -> Decimal:
    sum = 0

    for income in obj.incomes:
        if (income.status == IncomeStatus.PAID):
            sum += income.value

    return to_dec(sum)


def calc_interest_total(obj) -> Decimal:
    sum = 0

    for income in obj.incomes:
        sum += income.value

    return to_dec(sum)


def calc_effective_annual_rate(obj) -> Decimal:
    days = obj.duration
    if(obj.interest_term == InterestTerms.END_OF_TERM):
        m = to_dec(365/days)        # выплат в год
    else:
        m = 12
    
    r = obj.nominal_rate / 100      # номинальная ставка

    EAR = pow(1+r/m, m) - 1         # эффективная ставка
    
    return to_dec(EAR*100)
