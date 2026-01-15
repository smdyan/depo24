from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.reference.model.bank import Bank, BankCreate, BankPublic


router = APIRouter(prefix="/refs", tags=["refs"])


@router.get("/banks/", response_model=list[BankPublic])
async def getAllBanks(session: SessionDep):
    obj_list = session.exec(select(Bank)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="banks not found")
    return obj_list


@router.get("/banks/{id:int}", response_model=BankPublic)
async def getBank(id: int, session: SessionDep):
    obj = session.get( Bank, id )
    if not obj:
        raise HTTPException(status_code=404, detail="bank not found")
    return obj



