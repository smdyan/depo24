from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit

class CurrencyBase(SQLModel):
    short_name: str
    full_name: str
    country: str
    

class Currency(CurrencyBase, table=True):
    id: int = SQLField(default=None, primary_key=True)
    deposits: Optional[list["Deposit"]] = Relationship(back_populates="currency")


class CurrencyPublic(CurrencyBase):
    id: int


class CurrencyCreate(CurrencyBase):
    pass

