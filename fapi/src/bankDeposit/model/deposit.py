from sqlmodel import SQLModel, Field, Relationship
from pydantic import computed_field, Field as PydanticField
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.service.finance import calc_gross_value, calc_effective_int_rate
from pydantic import ConfigDict


if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income
    from src.bankDeposit.model.income import IncomePublic
else:
    # Ensure Income models are registered with SQLModel at runtime
    from src.bankDeposit.model import income as _income  # noqa: F401

    Income = _income.Income
    IncomePublic = _income.IncomePublic


class DepositBase(SQLModel):
    bank_name: str
    client_name: str
    description: str
    duration: int
    date_open: date
    date_close: Optional[date] = None
    face_value: int
    interest_rate: int
    income_value: Optional[int] = None


class Deposit(DepositBase, table=True):
    id: int = Field( default=None, primary_key=True )
    incomes: Optional[list["Income"]] = Relationship( back_populates="deposit" )    # "deposit" is a name of the attribute in the other model class "Income"

class DepositCreate(SQLModel):
    model_config = {"extra": "forbid"}

    bank_name: str
    client_name: str
    description: str
    duration: int
    date_open: date
    face_value: int
    interest_rate: int
    interest_term: int       #не сохраняется в бд


class DepositPublic(DepositBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

    @computed_field(return_type=int)
    def effective_interest_rate(self) -> int:     #с учетом капитализации
        return calc_effective_int_rate(self)

    @computed_field(return_type=int)
    def gross_value(self) -> int:
        return calc_gross_value(self)
    
class DepositPublicWithIncome(DepositPublic):
    incomes: list["IncomePublic"] = PydanticField(default_factory=list)
