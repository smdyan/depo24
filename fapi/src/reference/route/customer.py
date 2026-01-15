from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.reference.model.customer import Customer, CustomerCreate, CustomerPublic


router = APIRouter(prefix="/refs", tags=["refs"])


@router.get("/customers/", response_model=list[CustomerPublic])
async def getAllCustomers(session: SessionDep):
    obj_list = session.exec(select(Customer).where(Customer.status == True)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="customers not found")
    return obj_list


@router.get("/customers/archived", response_model=list[CustomerPublic])
async def getAllCustomers(session: SessionDep):
    obj_list = session.exec(select(Customer).where(Customer.status == False)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="customers not found")
    return obj_list


@router.get("/customers/{id:int}", response_model=CustomerPublic)
async def getCustomer(id: int, session: SessionDep):
    obj = session.get( Customer, id )
    if not obj:
        raise HTTPException(status_code=404, detail="customer not found")
    return obj



