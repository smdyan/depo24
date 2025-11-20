from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.misc.model.bank import Bank, BankCreate, BankPublic


router = APIRouter(prefix="/banks", tags=["banks"])


@router.post("/")
def addBank(payload: BankCreate, session: SessionDep):
    obj = Bank(**payload.model_dump(exclude_none=True))
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {"ok": True}


@router.delete("/{id}")
async def deleteCurrency(id: int, session: SessionDep):
    obj = session.get(Bank, id)
    if not obj:
        raise HTTPException(status_code=404, detail="bank not found")
    session.delete(obj)
    session.commit()
    return {"ok": True}


@router.get("/", response_model=list[BankPublic])
async def getAllBanks(session: SessionDep):
    obj_list = session.exec(select(Bank)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="banks not found")
    return obj_list


@router.get("/{id:int}", response_model=BankPublic)
async def getBank(id: int, session: SessionDep):
    obj = session.get( Bank, id )
    if not obj:
        raise HTTPException(status_code=404, detail="bank not found")
    return obj



