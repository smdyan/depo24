from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.service.deposit_parameters import (
    calc_interest_accured,
    calc_interest_paid,
    calc_interest_total,
    calc_effective_annual_rate,
)
from src.bankDeposit.model.deposit_parameters import InterestTerms, DepositStatus

if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income
    from src.bankDeposit.model.income import IncomePublic
else:
    from src.bankDeposit.model import income as _income                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime

    Income = _income.Income
    IncomePublic = _income.IncomePublic


class DepositBase(SQLModel):
    bank_name: str          #сейчас произвольное название, переделать на значение из БД "customer_id"
    client_name: str        #тоже
    description: str
    duration: int
    date_open: date
    date_close: Optional[date] = None
    currency: str
    principal_value: Decimal = Field(
        max_digits=12,
        decimal_places=2,
    )
    topup_value: Decimal = Field(
        max_digits=12,
        decimal_places=2,
    )
    nominal_rate: Decimal = Field(
        max_digits=5,
        decimal_places=2,
    )
    interest_term: InterestTerms
    status: DepositStatus = Field(default="active")                                 #изменение статуса сопровождать проводкой


class Deposit(DepositBase, table=True):
    id: int = Field( default=None, primary_key=True )
    incomes: Optional[list["Income"]] = Relationship( back_populates="deposit" )    # "deposit" is a name of the attribute in the other model class "Income"


class DepositCreate(DepositBase):
    model_config = {"extra": "forbid"}


class DepositPublic(DepositBase):
    id: int

    @computed_field(return_type=int)
    def interest_accured(self) -> int:          #начислено
        return calc_interest_accured(self)

    @computed_field(return_type=int)
    def interest_paid(self) -> int:                #выплачено
        return calc_interest_paid(self)
    
    @computed_field(return_type=int)
    def interest_total(self) -> int:                #общая сумма процентов по вкладу
        return calc_interest_total(self)
    
    @computed_field(return_type=int)
    def effective_rate(self) -> Decimal:            #EAR
        return calc_effective_annual_rate(self)


class DepositPublicWithIncome(DepositPublic):
    incomes: list["IncomePublic"] = PydanticField(default_factory=list)
