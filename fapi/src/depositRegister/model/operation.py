from sqlmodel import SQLModel, Relationship, Field as SQLField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.depositRegister.model.parameters import DepositOperationType

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit


class OperationBase(SQLModel):
    deposit_id: int | None = SQLField(default=None, foreign_key="deposit.id")       #"deposit" is the default name of the table in the database
    ledger_transaction_id: int
    operation_type: DepositOperationType
    amount: Decimal | None = SQLField(default=None)
    operation_date: date
    description: str



class Operation(OperationBase, table=True):
    id: int = SQLField(default=None, primary_key=True)
    deposit: Optional["Deposit"] = Relationship(back_populates="operations")

class OperationPublic(OperationBase):
    id: int

class OperationCreate(OperationBase):
    pass

