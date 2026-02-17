from enum import Enum, IntEnum

class ProductType(str, Enum):                   # тут временно, вынести в за границы депозита 
    DEPOSIT = "deposit"

class InterestTerms(str, Enum):
    END_OF_TERM = "end_of_term"                 # выплата % в конце срока вклада
    MONTHLY = "monthly"                         # выплата % ежемесячно

class PeriodAnchor(str, Enum):
    CALENDAR_MONTH = "calendar_month"           # рассчеты производятся 1 числа месяца
    DEPOSIT_DATE = "deposit_open_date"          # расчеты ежемесячно с даты открытия счета


class InterestModes(str, Enum):
    PAYOUT = "payout"                           # выплата % на расчетный счет
    CAPITALIZE = "capitalize"                   # причисление % к сумме вклада


class DepositStatus(str, Enum):
    CLOSED = "closed"
    ACTIVE = "active"
    
    
class DepositOperationType(str, Enum):
    OPEN = "open"
    TOPUP = "topup"
    WITHDRAWAL = "withdrawal"                       # no
    INTEREST_ACCRUAL = "interest_accrual"
    INTEREST_CAPITALIZE = "interest_capitalize"
    INTEREST_PAYOUT = "interest_payout"
    CLOSE = "close"
    EARLY_CLOSE = "early_close"                     # no
    CORRECTION = "correction"                       # no
    CHANGE_DURATION = "change_duration"             # no
    CHANGE_RATE = "change_rate"

