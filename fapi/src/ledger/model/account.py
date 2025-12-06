from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, List, TYPE_CHECKING
from src.ledger.model.parameters import (
    AccountLevel, AccountType, AccountStatus
)
if TYPE_CHECKING:
    from src.ledger.model.entry import Entry, EntryPublic
else:
    from src.ledger.model import entry as _entry                     # noqa: F401 # Ensure Entry models are registered with SQLModel at runtime
    Entry = _entry.Entry
    EntryPublic = _entry.EntryPublic


class  AccountBase(SQLModel):
    name: str
    code: int
    level: AccountLevel
    type: AccountType
    status: Optional[AccountStatus] = SQLField(default=AccountStatus.ENABLED) 
    parent_id: Optional[int] = SQLField(default=None, foreign_key="account.id")


class Account(AccountBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    parent: Optional["Account"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Account.id"}                        # remote_side указывает на сторону “родителя”.
    )
    children: Optional[List["Account"]] = Relationship(back_populates="parent")
    debit_entries: list["Entry"] = Relationship(
        back_populates="debit_account",
        sa_relationship_kwargs={"foreign_keys": "[Entry.debit_account_id]"},
    )
    credit_entries: list["Entry"] = Relationship(
        back_populates="credit_account",
        sa_relationship_kwargs={"foreign_keys": "[Entry.credit_account_id]"},
    )


class AccountCreate(AccountBase):
    parent_name: str | None = None


class AccountPublic(AccountBase):
    id: int

