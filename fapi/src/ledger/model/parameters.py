from enum import Enum, IntEnum


class AccountLevel(IntEnum):
    CLAUSE_0 = 0                 # раздел плана счетов
    SYNTHETIC_1 = 1              # синтетический счет первого порядка
    SYNTHETIC_2 = 2              # синтетический субсчет второго порядка
    ANALYTIC_3 = 3               # аналитический субсчет третьего порядка


class AccountType(str, Enum):
    ASSET = "active"                    # активный счет
    LIABILITY = "passive"               # пассивный счет
    HYBRID = "active_passive"           # активно-пассивный счет

class AccountStatus(IntEnum):
    DISABLED = 0
    ENABLED = 1

class TransactionType(str, Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"
    INTEREST_ACCRUAL = "interest_accrual"
    INTEREST_CAPITALIZE = "interest_capitalize"
    INTEREST_PAYOUT = "interest_payout"
    FEE = "fee"
    CORRECTION = "correction"
    REVERSAL = "reversal"

class ProductType(str, Enum):
    DEPOSIT_TERM = "deposit_term"
    DEPOSIT_SAVINGS = "deposit_savings"
    CARD_DEBIT = "card_debit"
    CARD_CREDIT = "card_credit"
    MORTGAGE = "mortgage"

class TransactionStatus(str, Enum):
    PENDING = "pending"                 # создана, но не проведена
    POSTED = "posted"                   # проведена, проводки в журнале
    REVERSED = "reversed"               # сторнирована