from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from datetime import date

if TYPE_CHECKING:
    from src.ledger.model.account import Account
    from src.ledger.model.transaction import Transaction


class  EntryBase(SQLModel):
    transaction_id: int = SQLField(foreign_key="transaction.id")
    debit_account_id: int = SQLField(foreign_key="account.id")
    credit_account_id: int = SQLField(foreign_key="account.id")
    amount: Decimal
    date: date
    description: str | None = None


class Entry(EntryBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    transaction: Optional["Transaction"] = Relationship(back_populates="entries")
    debit_account: Optional["Account"] = Relationship(
        back_populates="debit_entries",
        sa_relationship_kwargs={"foreign_keys": "[Entry.debit_account_id]"},
    )
    credit_account: Optional["Account"] = Relationship(
        back_populates="credit_entries", 
        sa_relationship_kwargs={"foreign_keys": "[Entry.credit_account_id]"},
    )


class EntryCreate(EntryBase):
    model_config = {"extra": "forbid"}


class EntryPublic(EntryBase):
    id: int
