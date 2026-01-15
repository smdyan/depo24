from enum import Enum
from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import date
# from src.depositRegister.service.parameters import (
#     calc_interest_paid,
#     calc_interest_total,
#     calc_effective_annual_rate,
# )
from src.depositRegister.model.parameters import (
    InterestTerms, PeriodAnchor, InterestPayout, DepositStatus )

if TYPE_CHECKING:
    from src.reference.model.customer import Customer, CustomerPublic
    from src.reference.model.bank import Bank, BankPublic
    from src.depositRegister.model.operation import Operation, OperationPublic
else:
    from src.reference.model import customer as _customer       # noqa: F401
    Customer = _customer.Customer
    CustomerPublic = _customer.CustomerPublic

    from src.reference.model import bank as _bank               # noqa: F401
    Bank = _bank.Bank
    BankPublic = _bank.BankPublic

    from src.depositRegister.model import operation as _operation     # noqa: F401
    Operation = _operation.Operation
    OperationPublic = _operation.OperationPublic


class DepositBase(SQLModel):
    bank_id: int = SQLField(foreign_key="bank.id")
    customer_id: int = SQLField(foreign_key="customer.id")
    description: str | None = SQLField(default=None, nullable=True)
    currency_code: str | None = SQLField(default="RUR")
    interest_term: InterestTerms
    interest_payout: InterestPayout | None = SQLField(default=None)
    interest_basis: PeriodAnchor | None = SQLField(default=PeriodAnchor.CALENDAR_MONTH)
    nominal_rate: Decimal = SQLField(sa_column=Column(Numeric(5, 2)))
    duration: int                                                                                   # Если 0, то вклад до востребования
    date_open: date
    date_close: date | None = SQLField(default=None, nullable=True)
    principal_value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))                           # Текущие агрегаты (для быстрого чтения). Истина — журнал операций.
    topup_value: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))             # тоже
    capitalized_value: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))       # тоже
    accrued_value: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))           # тоже
    status: DepositStatus | None = SQLField(default=DepositStatus.ACTIVE)


class Deposit(DepositBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    customer: Optional["Customer"] = Relationship(back_populates="deposits")                        # "deposits" is a name of the attribute in the other model class "Customer"
    bank: Optional["Bank"] = Relationship(back_populates="deposits")
    operations: Optional[List["Operation"]] = Relationship(back_populates="deposit")                # "deposit" is a name of the attribute in the other model class "Operation"
    date_last_accruel: Optional[date]

class DepositCreate(DepositBase):
    model_config = {"extra": "forbid"}


class DepositPublic(DepositBase):
    id: int
   
    customer_id: int | None = PydanticField(exclude=True)
    
    customer: Optional["CustomerPublic"] = PydanticField(default=None, exclude=True)
    
    @computed_field(return_type=str | None)
    def customer_name(self) -> str | None:
        if self.customer is None:
            return None
        return f"{self.customer.second_name} {self.customer.first_name} {self.customer.middle_name}"
    
    bank: Optional["BankPublic"] = PydanticField(default=None, exclude=True)
   
    bank_id: int | None = PydanticField(exclude=True)
    
    @computed_field(return_type=str | None)
    def bank_name(self) -> str | None:
        if self.bank is None:
            return None
        return f"{self.bank.short_name}"
    
    # @computed_field(return_type=Decimal)
    # def interest_paid(self) -> Decimal:                 # выплачено %
    #     return calc_interest_paid(self)
    
    # @computed_field(return_type=Decimal)
    # def interest_total(self) -> Decimal:                # сумма % в конце срока
    #     return calc_interest_total(self)
    
    # @computed_field(return_type=Decimal)
    # def effective_rate(self) -> Decimal:                # EAR
    #     return calc_effective_annual_rate(self)


class DepositPublicWithOps(DepositPublic):
    operations: List["OperationPublic"] = PydanticField(default_factory=list)


# DepositPublicWithOps.model_rebuild()
