from sqlmodel import SQLModel, Field
from pydantic import computed_field
from typing import Optional
from datetime import date
from src.service.finance import calc_gross_value, calc_effective_int_rate


class BankDepositBase( SQLModel ):
    bankName: str
    clientName: str
    duration: int
    interestRate: int
    dateOpen: date
    dateClose: Optional[date] = None
    faceValue: int
    incomeValue: Optional[int] = None
    description: str


class BankDeposit( BankDepositBase, table=True ):
    id: int = Field( default=None, primary_key=True )


class BankDepositCreate( SQLModel ):
    model_config = {"extra": "forbid"}

    bankName: str
    clientName: str
    duration: int
    interestRate: int
    interestTerm: int       #не сохраняется в бд
    dateOpen: date
    faceValue: int
    description: str

class BankDepositPublic( BankDepositBase ): #заменить входной параметр на базовый
    id: int
    
    @computed_field(return_type=int)
    def effectiveInterestRate(self) -> int:     #с учетом капитализации
        return calc_effective_int_rate(self)

    @computed_field(return_type=int)
    def grossValue(self) -> int:
        return calc_gross_value(self)
