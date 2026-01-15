from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.reference.model.currency import Currency, CurrencyPublic


router = APIRouter(prefix="/refs", tags=["refs"])


@router.get("/currencies/", response_model=list[CurrencyPublic])
async def getAllCurrencies(session: SessionDep):
    obj_list = session.exec(select(Currency)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="currency not found")
    return obj_list


@router.get("/currencies/{id:int}", response_model=CurrencyPublic)
async def getCurrency(id: int, session: SessionDep):
    obj = session.get( Currency, id )
    if not obj:
        raise HTTPException(status_code=404, detail="currency not found")
    return obj



