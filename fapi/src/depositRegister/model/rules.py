from enum import Enum
from src.depositRegister.model.parameters import ProductType, DepositOperationType

# логические коды счетов
class LogicalAccount(str, Enum):
    CASH = "cash_account"
    DEPOSIT = "deposit_account"
    ACCRUED_INTEREST = "accrued_interest"

POSTING_TEMPLATES = {
    (ProductType.DEPOSIT, DepositOperationType.OPEN): [
        {"debit": LogicalAccount.DEPOSIT,
         "credit": LogicalAccount.CASH}
    ],
        (ProductType.DEPOSIT, DepositOperationType.CLOSE): [
        {"debit": LogicalAccount.DEPOSIT,
         "credit": LogicalAccount.CASH}
    ],
}