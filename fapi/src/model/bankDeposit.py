from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class BankDepositBase( SQLModel ):
    bankName: str
    clientName: str
    duration: int
    interestRate: int
    dateOpen: date
    dateClose: Optional[date] = None
    faceValue: int
    interestValue: Optional[int] = None
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

class BankDepositPublic( BankDeposit ):
    # interestRateEffective: int        #с учетом капитализации
    pass
