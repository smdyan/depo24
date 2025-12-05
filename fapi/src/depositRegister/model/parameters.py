from enum import Enum, IntEnum


class InterestTerms(IntEnum):
    END_OF_TERM = 1               # выплата % в конце срока вклада
    MONTHLY_COMPOUND = 2          # капитализация % ко вкладу ежемесячно
    MONTHLY_PAYOUT = 3            # выплата % на расчетный счет ежемесячно
    VALLET = 4                    # начисление % ежедневно на остаток средств, выплата ежемесячно


class InterestBasis(IntEnum):
    CALENDAR_MONTH = 1              # рассчеты производятся 1 числа, на минимальную сумму за период
    OPEN_DATE = 2                   # расчеты ежемесячно с даты открытия счета
    DAYLY = 3                       # начисление ежедневно

class Withdrawal(str, Enum):
    NOT_ALLOWED = "not_allowed"
    ALLOWED = "allowed"                     # 
    LIMITED = "limited"                     # в пределах неснижаемого остатка

class DepositStatus(IntEnum):
    CLOSED = 0
    ACTIVE = 1                      # действующий вклад
    
    @property
    def is_active(self) -> bool:
        return self is DepositStatus.ACTIVE
    

class IncomeStatus(str, Enum):
    PENDING = "pending"             # предстоящая выплата %
    PAID = "paid"

    @property
    def is_pending(self) -> bool:
        return self is IncomeStatus.PENDING
    

class DepositOperationType(str, Enum):
    OPEN = "open"
    INITIAL_DEPOSIT = "initial_deposit"
    TOPUP = "topup"
    WITHDRAWAL_PARTIAL = "withdrawal_partial"
    WITHDRAWAL_FULL = "withdrawal_full"
    INTEREST_ACCRUAL = "interest_accrual"
    INTEREST_CAPITALIZE = "interest_capitalize"
    INTEREST_PAYOUT = "interest_payout"
    RENEWAL = "renewal"
    CLOSE = "close"
    EARLY_CLOSE = "early_close"
    FEE = "fee"
    CORRECTION = "correction"