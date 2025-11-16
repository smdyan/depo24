from enum import Enum
from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.service.deposit_parameters import (
    calc_interest_accrued,
    calc_interest_paid,
    calc_interest_total,
    calc_effective_annual_rate,
)
from src.bankDeposit.model.deposit_parameters import InterestTerms, DepositStatus
from src.misc.model.customer import Customer

if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income, IncomePublic
    from src.misc.model.customer import Customer, CustomerPublic
else:
    from src.bankDeposit.model import income as _income                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime
    Income = _income.Income
    IncomePublic = _income.IncomePublic

    from src.misc.model import customer as _customer
    Customer = _customer.Customer
    CustomerPublic = _customer.CustomerPublic


class DepositBase(SQLModel):
    bank_name: str          #сейчас произвольное название, переделать на значение из БД
    customer_id: int | None = SQLField(default=None, foreign_key="customer.id")
    description: str
    duration: int
    date_open: date
    date_close: date | None = SQLField(default=None, nullable=True)
    currency: str
    principal_value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))
    topup_value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))
    nominal_rate: Decimal = SQLField(sa_column=Column(Numeric(5, 2)))
    interest_term: InterestTerms
    status: DepositStatus = SQLField(default=DepositStatus.ACTIVE)                                 #изменение статуса сопровождать проводкой


class Deposit(DepositBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    incomes: list["Income"] = Relationship(back_populates="deposit")                # "deposit" is a name of the attribute in the other model class "Income"
    customer: Optional["Customer"] = Relationship(back_populates="deposits")           # "deposits" is a name of the attribute in the other model class "Customer"


class DepositCreate(DepositBase):
    model_config = {"extra": "forbid"}


class DepositPublic(DepositBase):
    id: int
    customer: Optional["CustomerPublic"] = PydanticField(default=None, exclude=True)
    customer_id: int | None = PydanticField(exclude=True)

    @computed_field(return_type=str | None)
    def customer_name(self) -> str | None:
        if self.customer is None:
            return None
        return f"{self.customer.last_name} {self.customer.first_name}"

    @computed_field(return_type=Decimal)
    def interest_accrued(self) -> Decimal:          #начислено
        return calc_interest_accrued(self)

    @computed_field(return_type=Decimal)
    def interest_paid(self) -> Decimal:                #выплачено
        return calc_interest_paid(self)
    
    @computed_field(return_type=Decimal)
    def interest_total(self) -> Decimal:                #общая сумма процентов по вкладу
        return calc_interest_total(self)
    
    @computed_field(return_type=Decimal)
    def effective_rate(self) -> Decimal:                #EAR
        return calc_effective_annual_rate(self)


class DepositPublicWithIncome(DepositPublic):
    incomes: list["IncomePublic"] = PydanticField(default_factory=list)
