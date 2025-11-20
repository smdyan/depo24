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

if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income, IncomePublic
    from src.misc.model.customer import Customer, CustomerPublic
    from src.misc.model.currency import Currency, CurrencyPublic
    from src.misc.model.bank import Bank, BankPublic
else:
    from src.bankDeposit.model import income as _income                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime
    Income = _income.Income
    IncomePublic = _income.IncomePublic

    from src.misc.model import customer as _customer
    Customer = _customer.Customer
    CustomerPublic = _customer.CustomerPublic

    from src.misc.model import currency as _currency
    Currency = _currency.Currency
    CurrencyPublic = _currency.CurrencyPublic

    from src.misc.model import bank as _bank
    Bank = _bank.Bank
    BankPublic = _bank.BankPublic


class DepositBase(SQLModel):
    bank_id: int = SQLField(foreign_key="bank.id")
    customer_id: int = SQLField(foreign_key="customer.id")
    description: str | None = SQLField(default=None, nullable=True)
    duration: int
    date_open: date
    date_close: date | None = SQLField(default=None, nullable=True)
    currency_id: int | None = SQLField(default=None, foreign_key="currency.id")
    principal_value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))
    topup_value: Decimal | None = SQLField(default=None, sa_column=Column(Numeric(12, 2)))
    nominal_rate: Decimal = SQLField(sa_column=Column(Numeric(5, 2)))
    interest_term: InterestTerms
    status: DepositStatus | None = SQLField(default=DepositStatus.ACTIVE)                                 #изменение статуса сопровождать проводкой


class Deposit(DepositBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    incomes: list["Income"] = Relationship(back_populates="deposit")                # "deposit" is a name of the attribute in the other model class "Income"
    customer: Optional["Customer"] = Relationship(back_populates="deposits")           # "deposits" is a name of the attribute in the other model class "Customer"
    currency: Optional["Currency"] = Relationship(back_populates="deposits")
    bank: Optional["Bank"] = Relationship(back_populates="deposits")


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
        return f"{self.customer.second_name} {self.customer.first_name}"
    
    currency: Optional["CurrencyPublic"] = PydanticField(default=None, exclude=True)
    currency_id: int | None = PydanticField(exclude=True)
    @computed_field(return_type=str | None)
    def currency_name(self) -> str | None:
        if self.currency is None:
            return None
        return f"{self.currency.short_name}"
    
    bank: Optional["BankPublic"] = PydanticField(default=None, exclude=True)
    bank_id: int | None = PydanticField(exclude=True)
    @computed_field(return_type=str | None)
    def bank_name(self) -> str | None:
        if self.bank is None:
            return None
        return f"{self.bank.short_name}"
    
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
