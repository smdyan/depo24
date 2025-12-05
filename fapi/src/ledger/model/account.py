from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, Field as PydanticField
from typing import Optional, List, TYPE_CHECKING
from src.ledger.model.parameters import (
    AccountLevel, AccountType, AccountStatus
)
from src.ledger.service.parameters import get_children
# if TYPE_CHECKING:
#     from src.ledger.model.entry import Entry, EntryPublic
# else:
#     from src.ledger.model import entry as _entry                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime
#     Entry = _entry.Entry
#     EntryPublic = _entry.EntryPublic


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


class AccountCreate(AccountBase):           # parent_name,name,level,code,type
    parent_name: str | None = None


class AccountPublic(AccountBase):
    id: int

