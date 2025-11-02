from enum import Enum, IntEnum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import computed_field, Field as PydanticField
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from datetime import date
from src.bankDeposit.service.deposit_parameters import calc_gross_value, calc_effective_interest_rate, calc_total_income

if TYPE_CHECKING:
    from src.bankDeposit.model.income import Income
    from src.bankDeposit.model.income import IncomePublic
else:
    from src.bankDeposit.model import income as _income                     # noqa: F401 # Ensure Income models are registered with SQLModel at runtime

    Income = _income.Income
    IncomePublic = _income.IncomePublic


class InterestTerms(IntEnum):
    END_OF_TERM = 1               # в конце срока (простые проценты, без капитализации)
    MONTHLY_COMPOUNDING = 2       # ежемесячно с капитализацией
    MONTHLY_PAYOUT = 3            # ежемесячно с выплатой (без капитализации)

class DepositStatus(Enum):
    ACTIVE = "active"
    CLOSE = "close"

    @property
    def is_active(self) -> bool:
        return self is DepositStatus.ACTIVE

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
    nominal_rate: Decimal = Field(
        max_digits=5,
        decimal_places=2,
    )
    interest_term: InterestTerms
    status: DepositStatus = Field(default="active") #изменение статуса сопровождать проводкой


class Deposit(DepositBase, table=True):
    id: int = Field( default=None, primary_key=True )
    incomes: Optional[list["Income"]] = Relationship( back_populates="deposit" )    # "deposit" is a name of the attribute in the other model class "Income"


class DepositCreate(DepositBase):
    model_config = {"extra": "forbid"}


class DepositPublic(DepositBase):
    id: int

    @computed_field(return_type=int)
    def interest_accured(self) -> int:
        return 1

    @computed_field(return_type=int)
    def interest_capitalized(self) -> int:
        return 2

    @computed_field(return_type=int)
    def nterest_paid(self) -> int:
        return 3
    
    @computed_field(return_type=int)
    def effective_rate(self) -> Decimal:     #с учетом капитализации
        # return calc_effective_interest_rate(self)
        return 4


class DepositPublicWithIncome(DepositPublic):
    incomes: list["IncomePublic"] = PydanticField(default_factory=list)

