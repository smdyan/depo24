from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.bankDeposit.model.deposit import Deposit

class BankBase(SQLModel):
    short_name: str
    full_name: str
    address: str | None = SQLField(default=None)
    status: bool = SQLField(default=True)
    

class Bank(BankBase, table=True):
    id: int = SQLField(default=None, primary_key=True)
    deposits: Optional[list["Deposit"]] = Relationship(back_populates="bank")


class BankPublic(BankBase):
    id: int


class BankCreate(BankBase):
    pass

