from enum import Enum
from sqlmodel import SQLModel, Relationship, Field as SQLField
from typing import Optional, TYPE_CHECKING
from pydantic import computed_field

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit

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

    @computed_field(return_type=str | None)
    def full_name(self) -> str | None:
        return f"{self.second_name} {self.first_name}"


class CustomerCreate(CustomerBase):
    pass

