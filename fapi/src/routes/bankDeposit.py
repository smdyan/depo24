from typing import Annotated
from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.data.init import SessionDep
from src.model.bankDeposit import BankDeposit, BankDepositCreate, BankDepositPublic
from src.utils.calcDepositCloseDate import calcDepositCloseDate
from src.utils.calcDepositIntValue import calcDepositIntValue



router = APIRouter( prefix="/deposit" )


@router.post( "/", response_model=BankDepositPublic )
def addBankDeposit( payload: BankDepositCreate, session: SessionDep ):
    #obj = BankDeposit.model_validate( payload )
    obj = BankDeposit(**payload.model_dump(exclude_none=True))
    obj.dateClose = calcDepositCloseDate(obj.dateOpen, obj.duration)
    obj.interestValue = calcDepositIntValue(obj.faceValue, obj.interestRate, obj.duration, payload.interestTerm)
    
    session.add( obj )
    session.commit()
    session.refresh( obj )
    return obj


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
    obj = session.get( BankDeposit, id )
    if not obj:
        raise HTTPException(status_code=404, detail="deposit not found")
    return obj
