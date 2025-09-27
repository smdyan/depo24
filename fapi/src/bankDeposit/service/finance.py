from datetime import date, timedelta

def calc_income_value(faceValue: int, interestRate: int, duration: int, interestTerm: int) -> int:
    if (interestTerm != 1): return 0

    n = faceValue * (interestRate/100) * (duration/365)
    return int(n)

def calc_gross_value(obj) -> int:
    return obj.faceValue + obj.incomeValue

def calc_effective_int_rate(obj) -> int:
    n= (obj.incomeValue/obj.duration*365)/obj.faceValue*100
    return int(n)
