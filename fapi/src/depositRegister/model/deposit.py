from enum import Enum
from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Relationship, Field as SQLField
from pydantic import computed_field, PrivateAttr, Field as PydanticField
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from datetime import date
from src.depositRegister.service.deposit_analysis import get_deposit_analysis, AnalysisResult
from src.depositRegister.model.enums import (
    InterestTerms, PeriodAnchor, InterestModes, DepositStatus
)

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
    interest_period_basis: PeriodAnchor | None = SQLField(default=PeriodAnchor.CALENDAR_MONTH)
    interest_mode: InterestModes | None = SQLField(default=None)
    nominal_rate: Decimal = SQLField(sa_column=Column(Numeric(5, 2)))
    duration: int                                                                                   # Если 0, то вклад до востребования
    date_open: date
    date_close: date | None = SQLField(default=None, nullable=True)
    date_last_accrual: date | None = SQLField(default=None, nullable=True)
    principal_value: Decimal = SQLField(sa_column=Column(Numeric(12, 2)))                           # Текущие агрегаты (для быстрого чтения). Истина — журнал операций.
    topup_value: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))             # тоже
    capitalized_income: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))      # тоже
    paid_income: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))             # тоже. сумма выплаченых начислений
    paid_principal: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 2)))          # тоже. сумма тела вклада и пополнений
    accrued_value: Decimal | None = SQLField(default=0, sa_column=Column(Numeric(12, 4)))           # тоже
    balancedays_base: Decimal| None = SQLField(default=0, sa_column=Column(Numeric(14, 4)))         # base balance days at last accurual date
    balancedays_cost: Decimal| None = SQLField(default=0, sa_column=Column(Numeric(14, 4)))         # contrubution balance days at last accurual date
    status: DepositStatus | None = SQLField(default=DepositStatus.ACTIVE)


class Deposit(DepositBase, table=True):
    id: int = SQLField( default=None, primary_key=True )
    customer: Optional["Customer"] = Relationship(back_populates="deposits")                        # "deposits" is a name of the attribute in the other model class "Customer"
    bank: Optional["Bank"] = Relationship(back_populates="deposits")
    operations: Optional[List["Operation"]] = Relationship(back_populates="deposit")                # "deposit" is a name of the attribute in the other model class "Operation"


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
        return f"{self.customer.full_name}"
    
    bank: Optional["BankPublic"] = PydanticField(default=None, exclude=True)
    bank_id: int | None = PydanticField(exclude=True)
    
    @computed_field(return_type=str | None)
    def bank_name(self) -> str | None:
        if self.bank is None:
            return None
        return f"{self.bank.short_name}"

    _analysis: Optional["AnalysisResult"] = PrivateAttr(default=None)

    def _get_analysis(self) -> "AnalysisResult":
        if self._analysis is None:
            as_of = self.date_last_accrual
            self._analysis = get_deposit_analysis(as_of, self)              # тут сидит ошибка, до первого акрула дата раньше на Т-1
        return self._analysis
    
    @computed_field(return_type=Decimal)
    def contributed_value(self) -> Decimal:
        return self._get_analysis().contributed_value
    
    @computed_field(return_type=Decimal)
    def balance_base(self) -> Decimal:
        return self._get_analysis().balance_base
    
    @computed_field(return_type=Decimal)
    def balance_average(self) -> Decimal:
        return self._get_analysis().balance_average
    
    @computed_field(return_type=Decimal)
    def income_realized(self) -> Decimal:
        return self._get_analysis().income_realized
    
    @computed_field(return_type=Decimal)
    def income_to_close(self) -> Decimal:
        return self._get_analysis().income_to_close
    
    @computed_field(return_type=Decimal)
    def apr_realized(self) -> Decimal:
        return self._get_analysis().apr_realized

    @computed_field(return_type=Decimal)
    def irr(self) -> Decimal:
        return self._get_analysis().irr
    
    @computed_field(return_type=Decimal)
    def ear_current(self) -> Decimal:
        return self._get_analysis().ear_current


class DepositPublicWithOps(DepositPublic):

    operations: List["OperationPublic"] = PydanticField(default_factory=list)
