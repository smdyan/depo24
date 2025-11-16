from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.misc.model.customer import Customer, CustomerCreate, CustomerPublic


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/")
def addCustomer(payload: CustomerCreate, session: SessionDep):
    obj = Customer(**payload.model_dump(exclude_none=True))
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {"ok": True}


@router.delete("/{id}")
async def deleteCustomer(id: int, session: SessionDep):
    obj = session.get(Customer, id)
    if not obj:
        raise HTTPException(status_code=404, detail="customer not found")
    session.delete(obj)
    session.commit()
    return {"ok": True}


@router.get("/", response_model=list[CustomerPublic])
async def getAllCustomers(session: SessionDep):
    obj_list = session.exec(select(Customer)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="customers not found")
    return obj_list


@router.get("/{id:int}", response_model=CustomerPublic)
async def getCustomer(id: int, session: SessionDep):
    obj = session.get( Customer, id )
    if not obj:
        raise HTTPException(status_code=404, detail="customer not found")
    return obj



