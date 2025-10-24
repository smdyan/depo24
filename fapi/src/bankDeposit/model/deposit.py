from sqlmodel import SQLModel, Field, Relationship
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.service.deposit_parameters import calc_gross_value, calc_effective_int_rate, calc_total_income

if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income
    from src.bankDeposit.model.income import IncomePublic
else:
    from src.bankDeposit.model import income as _income                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime

    Income = _income.Income
    IncomePublic = _income.IncomePublic


class DepositBase(SQLModel):
    bank_name: str
    client_name: str
    description: str
    duration: int
    date_open: date
    date_close: Optional[date] = None
    face_value: Decimal = Field(
        max_digits=12,
        decimal_places=2,
    )
    interest_rate: Decimal = Field(
        max_digits=5,
        decimal_places=2,
    )


class Deposit(DepositBase, table=True):
    id: int = Field( default=None, primary_key=True )
    incomes: Optional[list["Income"]] = Relationship( back_populates="deposit" )    # "deposit" is a name of the attribute in the other model class "Income"


class DepositCreate(DepositBase):
    model_config = {"extra": "forbid"}

    interest_term: int                              #не сохраняется в бд


class DepositPublic(DepositBase):
    id: int


class DepositPublicWithIncome(DepositPublic):
    incomes: list["IncomePublic"] = PydanticField(default_factory=list)

    @computed_field(return_type=int)
    def income_value(self) -> int:
        return calc_total_income(self)

    @computed_field(return_type=int)
    def gross_value(self) -> Decimal:
        return calc_gross_value(self)
    
    @computed_field(return_type=int)
    def effective_interest_rate(self) -> Decimal:     #с учетом капитализации
        return calc_effective_int_rate(self)