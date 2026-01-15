from enum import Enum
from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING
from src.depositRegister.model.parameters import IncomeStatus

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit
    from src.depositRegister.model.deposit import DepositPublic

class CustomerBase(SQLModel):
    first_name:     str
    second_name:    str
    middle_name:    str
    status:         bool = SQLField(default=True)
    

class Customer(CustomerBase, table=True):
    id: int = SQLField(default=None, primary_key=True)
    deposits: Optional[list["Deposit"]] = Relationship(back_populates="customer")


class CustomerPublic(CustomerBase):
    id: int


class CustomerCreate(CustomerBase):
    pass

