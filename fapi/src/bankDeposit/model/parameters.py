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

class Withdrawal(IntEnum):
    NOT_ALLOWED = 0
    ALLOWED = 1                     # 
    LIMITED = 2                     # в пределах неснижаемого остатка

class DepositStatus(IntEnum):
    CLOSED = 0
    ACTIVE = 1                      # действующий вклад
    
    @property
    def is_active(self) -> bool:
        return self is DepositStatus.ACTIVE
    

class IncomeStatus(IntEnum):
    PENDING = 1             # предстоящая выплата %
    PAID = 0

    @property
    def is_pending(self) -> bool:
        return self is IncomeStatus.PENDING