from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date


if TYPE_CHECKING:
    from src.bankDeposit.model.deposit import Deposit
    from src.bankDeposit.model.deposit import DepositPublic
else:
    # Ensure Income is registered with SQLModel at runtime for relationship resolution
    from src.bankDeposit.model import deposit as _deposit  # noqa: F401


class IncomeBase( SQLModel ):                                                   #parent data model
    value: int
    date_payment: date
    deposit_id: int | None = Field(default=None, foreign_key="deposit.id")       #"deposit" is the default name of the table in the database


class Income( IncomeBase, table=True ):                                         #table model
    id:int = Field( default=None, primary_key=True )
    deposit: Optional["Deposit"] = Relationship( back_populates="incomes" )     #"incomes" is a name of the attribute in the other model class "DepositBase", that references the current model

class IncomePublic( IncomeBase ):                                               #data model
    id: int

class IncomeCreate(IncomeBase):
    pass

class IncomePublicWithDeposit(IncomePublic):
    deposit: Optional["DepositPublic"] =Field(default = None)
