from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, Field as PydanticField
from typing import Optional, List, TYPE_CHECKING
from datetime import date
from src.ledger.model.parameters import (
    TransactionType, TransactionStatus, ProductType)

if TYPE_CHECKING:
    from src.ledger.model.entry import Entry, EntryPublic
else:
    from src.ledger.model import entry as _entry                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime
    Entry = _entry.Entry
    EntryPublic = _entry.EntryPublic


class  TransactionBase(SQLModel):
    transaction_type: TransactionType
    product_type: ProductType
    product_id: Optional[int] = SQLField(default=None, foreign_key="deposit.id")    #подумать над абстрактным классом "продукт"
    status: TransactionStatus = TransactionStatus.POSTED
    posted_at: date = SQLField(default_factory=date.utcnow)
    description: Optional[str] = None


class Transaction(TransactionBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    entries: List["Entry"] = Relationship(back_populates="transaction")


class TransactionCreate(TransactionBase):
    model_config = {"extra": "forbid"}


class AccountPublic(TransactionBase):
    id: int
