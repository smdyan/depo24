from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, List, TYPE_CHECKING
from datetime import date, datetime, timezone
from src.ledger.model.parameters import (
    TransactionType, TransactionStatus, ProductType)

if TYPE_CHECKING:
    from src.ledger.model.entry import Entry


class  TransactionBase(SQLModel):
    transaction_type: TransactionType
    product_type: ProductType
    product_id: Optional[int] = SQLField(default=None, foreign_key="deposit.id")    #подумать над абстрактным классом "продукт"
    status: TransactionStatus = TransactionStatus.POSTED
    posted_at: datetime = SQLField(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None


class Transaction(TransactionBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    entries: List["Entry"] = Relationship(back_populates="transaction")


class TransactionCreate(TransactionBase):
    model_config = {"extra": "forbid"}


class AccountPublic(TransactionBase):
    id: int
