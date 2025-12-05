from datetime import date, timedelta
from typing import List
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_FLOOR, getcontext, ROUND_HALF_UP, InvalidOperation
from src.depositRegister.model.income import Income, IncomeStatus
from src.depositRegister.model.parameters import InterestTerms
from src.depositRegister.service.utils import to_dec



def get_children(obj) -> List:
    days = obj.duration
    if(obj.interest_term == InterestTerms.END_OF_TERM):
        m = to_dec(365/days)        # выплат в год
    else:
        m = 12
    
    r = obj.nominal_rate / 100      # номинальная ставка

    EAR = pow(1+r/m, m) - 1         # эффективная ставка
    
    return to_dec(EAR*100)
