from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_FLOOR, getcontext, ROUND_HALF_UP, InvalidOperation
from src.depositRegister.service.utils import to_dec


def calc_close_date(date_open: date, duration: int) -> date:
    return date_open + timedelta(days=duration)


# def _calc_begin_date(date_payment: date, duration: int) -> date:
#     return date_payment - timedelta(days=duration)


# def calc_effective_annual_rate(obj) -> Decimal:
#     days = obj.duration
#     if(obj.interest_term == InterestTerms.END_OF_TERM):
#         m = to_dec(365/days)        # выплат в год
#     else:
#         m = 12
    
#     r = obj.nominal_rate / 100      # номинальная ставка

#     EAR = pow(1+r/m, m) - 1         # эффективная ставка
    
#     return to_dec(EAR*100)
