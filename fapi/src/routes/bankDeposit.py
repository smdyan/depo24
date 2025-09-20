from typing import Annotated
from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.data.init import SessionDep
from src.model.bankDeposit import BankDeposit, BankDepositCreate, BankDepositPublic


router = APIRouter( prefix="/deposit" )


@router.post( "/", response_model=BankDepositPublic )
def addBankDeposit( deposit: BankDepositCreate, session: SessionDep ):
    dbDeposit = BankDeposit.model_validate( deposit )
    session.add( dbDeposit )
    session.commit()
    session.refresh( dbDeposit )
    return dbDeposit


@router.delete("/{id}")
async def deleteBankDeposit( id: int, session: SessionDep ):
    deposit = session.get( BankDeposit, id )
    if not deposit:
        raise HTTPException(status_code=404, detail="bond not found")
    session.delete( deposit )
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=BankDepositPublic)
async def getBankDeposit(id: int, session: SessionDep):
    deposit = session.get( BankDeposit, id )
    if not deposit:
        raise HTTPException(status_code=404, detail="deposit not found")
    return deposit
