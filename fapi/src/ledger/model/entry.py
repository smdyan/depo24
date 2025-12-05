from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
# from src.ledger.service.parameters import ()

if TYPE_CHECKING:
    from src.ledger.model.account import Account, AccountPublic
    from src.ledger.model.transaction import Transaction, AccountPublic

else:
    from src.ledger.model import account as _account                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime
    Account = _account.Account
    AccountPublic = _account.AccontPublic


class  EntryBase(SQLModel):
    transaction_id: int = SQLField(foreign_key="transaction.id")
    debit_id: int = SQLField(foreign_key="account.id")
    credit_id: int = SQLField(foreign_key="account.id")
    amount: Decimal
    date: date
    description: str


class Entry(EntryBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    debit: Optional["Account"] = Relationship(back_populates="entries")                # "deposit" is a name of the attribute in the other model class "Income"
    credit: Optional["Account"] = Relationship(back_populates="entries")                # "deposit" is a name of the attribute in the other model class "Income"
    transaction: Optional["Transaction"] = Relationship(back_populates="entries")

class EntryCreate(EntryBase):
    model_config = {"extra": "forbid"}


class EntryPublic(EntryBase):
    id: int

