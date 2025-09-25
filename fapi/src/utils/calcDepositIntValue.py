from datetime import date, timedelta

def calcDepositIntValue(faceValue: int, interestRate: int, duration: int, interestTerm: int) -> int:
    if (interestTerm != 1): return 0

    n = faceValue * (interestRate/100) * (duration/365)
    return n
