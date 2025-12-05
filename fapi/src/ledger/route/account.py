from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.ledger.model.account import Account, AccountCreate, AccountPublic


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/")
def addAccount(payload: AccountCreate, session: SessionDep):
    obj = Account(**payload.model_dump(exclude_none=True))
    if(payload.parent_name != None):
        parent_obj = session.exec(select(Account).where(Account.name == payload.parent_name)).one()
        if not parent_obj:
            raise HTTPException(status_code=404, detail="parent_name not found")
        obj.parent_id = parent_obj.id
    
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {"ok": True}


@router.get("/", response_model=list[AccountPublic])
async def getAllAccounts(session: SessionDep):
    obj_list = session.exec(select(Account)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="account not found")
    return obj_list


@router.get("/{id:int}", response_model=AccountPublic)
async def getAccount(id: int, session: SessionDep):
    obj = session.get( Account, id )
    if not obj:
        raise HTTPException(status_code=404, detail="account not found")
    return obj



