from sqlmodel import SQLModel, Field
from datetime import date


class BankDepositBase( SQLModel ):
    bankName: str
    clientName: str
    duration: int
    interestRate: int
    interestPeriod: int
    dateOpen: date
    faceValue: int
    description: str
    status: bool


class BankDeposit( BankDepositBase, table=True ):
    id: int = Field( default=None, primary_key=True )


class BankDepositCreate( BankDepositBase ):
    pass

class BankDepositPublic( BankDepositBase ):
    id: int