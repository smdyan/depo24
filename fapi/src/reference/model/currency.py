from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING

# if TYPE_CHECKING:
#     from src.depositRegister.model.deposit import Deposit

class CurrencyBase(SQLModel):
    name: str
    country: str
    status: bool = SQLField(default=True)
    

class Currency(CurrencyBase, table=True):
    code: str = SQLField(primary_key=True)
    # deposits: Optional[list["Deposit"]] = Relationship(back_populates="currency")


class CurrencyPublic(CurrencyBase):
    code: str


class CurrencyCreate(CurrencyBase):
    code: str

