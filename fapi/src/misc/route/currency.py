from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.misc.model.currency import Currency, CurrencyCreate, CurrencyPublic


router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.post("/")
def addCurrency(payload: CurrencyCreate, session: SessionDep):
    obj = Currency(**payload.model_dump(exclude_none=True))
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {"ok": True}


@router.delete("/{id}")
async def deleteCurrency(id: int, session: SessionDep):
    obj = session.get(Currency, id)
    if not obj:
        raise HTTPException(status_code=404, detail="currency not found")
    session.delete(obj)
    session.commit()
    return {"ok": True}


@router.get("/", response_model=list[CurrencyPublic])
async def getAllCurrencies(session: SessionDep):
    obj_list = session.exec(select(Currency)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="currency not found")
    return obj_list


@router.get("/{id:int}", response_model=CurrencyPublic)
async def getCurrency(id: int, session: SessionDep):
    obj = session.get( Currency, id )
    if not obj:
        raise HTTPException(status_code=404, detail="currency not found")
    return obj



