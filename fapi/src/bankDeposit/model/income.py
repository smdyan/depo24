from enum import Enum
from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.model.parameters import IncomeStatus

if TYPE_CHECKING:
    from src.bankDeposit.model.deposit import Deposit


class IncomeBase(SQLModel):                                                   #parent data model
    value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))
    date_payment: date
    period: int
    status: IncomeStatus #изменение статуса сопроводить проводкой
    deposit_id: int | None = SQLField(default=None, foreign_key="deposit.id")    #"deposit" is the default name of the table in the database


class Income(IncomeBase, table=True):                                         #table model
    id: int = SQLField(default=None, primary_key=True)
    deposit: Optional["Deposit"] = Relationship(back_populates="incomes")     #"incomes" is a name of the attribute in the other model class "DepositBase", that references the current model

class IncomePublic(IncomeBase):                                               #data model
    id: int

class IncomeCreate(IncomeBase):
    pass

