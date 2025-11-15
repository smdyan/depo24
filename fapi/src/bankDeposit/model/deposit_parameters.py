from enum import Enum, IntEnum


class InterestTerms(IntEnum):
    END_OF_TERM = 1               # interest paid at end of term (simple interest, no compounding)
    MONTHLY_COMPOUND = 2          # interest compounded monthly
    MONTHLY_PAYOUT = 3            # interest paid out monthly without compounding


class DepositStatus(Enum):
    ACTIVE = "active"
    CLOSE = "close"

    @property
    def is_active(self) -> bool:
        return self is DepositStatus.ACTIVE
    

class IncomeStatus(Enum):
    PENDING = "pending"
    PAID = "paid"

    @property
    def is_pending(self) -> bool:
        return self is IncomeStatus.PENDING