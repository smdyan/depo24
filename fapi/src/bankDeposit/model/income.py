from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from src.bankDeposit.model.deposit import Deposit
    from src.bankDeposit.model.deposit import DepositPublic

class IncomeStatus(Enum):
    PENDING = "pending"
    PAID = "paid"

    @property
    def is_pending(self) -> bool:
        return self is IncomeStatus.PENDING

class IncomeBase(SQLModel):                                                   #parent data model
    value: Decimal = Field(
        max_digits=12,
        decimal_places=2,
    )
    date_payment: date
    period: int
    status: IncomeStatus #изменение статуса сопроводить проводкой
    deposit_id: int | None = Field(default=None, foreign_key="deposit.id")    #"deposit" is the default name of the table in the database


class Income(IncomeBase, table=True):                                         #table model
    id: int = Field(default=None, primary_key=True)
    deposit: Optional["Deposit"] = Relationship(back_populates="incomes")     #"incomes" is a name of the attribute in the other model class "DepositBase", that references the current model

class IncomePublic(IncomeBase):                                               #data model
    id: int

class IncomeCreate(IncomeBase):
    pass

class IncomePublicWithDeposit(IncomePublic):
    deposit: Optional["DepositPublic"] = Field(default=None)
