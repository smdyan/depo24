from fastapi import HTTPException, APIRouter
from sqlmodel import select
from typing import List
from src.database import SessionDep
from src.depositRegister.model.deposit import Deposit, DepositCreate, DepositPublicWithOps, DepositPublic
from src.depositRegister.errors import AccrualError
from src.depositRegister.service.parameters import calc_close_date
from src.depositRegister.service.operation_open import get_open_operation
from src.depositRegister.service.operation_accruel import calc_accruels


router = APIRouter(prefix="/deposits", tags=["deposits"])


@router.post("/")
def addDeposit(payload: DepositCreate, session: SessionDep):
    obj = Deposit(**payload.model_dump(exclude_none=True))
    
    obj.date_close = calc_close_date(obj.date_open, obj.duration)
    obj.date_last_accrual = obj.date_open
    
    operation = get_open_operation(obj)
    obj.operations.append(operation)
    
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return {"ok": True}


@router.delete("/{id}")
async def deleteDeposit(id: int, session: SessionDep):
    deposit = session.get(Deposit, id)
    if not deposit:
        raise HTTPException(status_code=404, detail="deposit not found")
    session.delete(deposit)
    session.commit()
    return {"ok": True}


@router.get("/", response_model=List[DepositPublic])    #type annotation
async def getAllDeposit(session: SessionDep):
    obj_list = session.exec(select(Deposit)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="deposits not found")
    return obj_list


@router.get("/{id:int}", response_model=DepositPublic)
async def getBankDeposit(id: int, session: SessionDep):
    obj = session.get( Deposit, id )
    if not obj:
        raise HTTPException(status_code=404, detail="deposit not found")
    return obj


@router.get("/{id:int}/ops", response_model=DepositPublicWithOps)
async def getBankDeposit(id: int, session: SessionDep):
    obj = session.get( Deposit, id )
    if not obj:
        raise HTTPException(status_code=404, detail="deposit not found")
    return obj


@router.post("/{id:int}/jobs")

async def doAccruels(id: int, session: SessionDep):
    obj = session.get( Deposit, id )
    
    try:
        result = calc_accruels(obj)
    except AccrualError as e:
        raise HTTPException(status_code=409, detail={"code": e.code, "message": str(e)})
    
    obj.operations.extend(result.operations)

    obj.date_last_accrual = result.last_accrual_date
    obj.accrued_value = result.accrued_value
    obj.principal_value = result.principal_value
    obj.topup_value = result.topup_value
    obj.capitalized_value = result.capitalized_value
    obj.paid_value = result.paid_value
    obj.status = result.status

    session.add(obj)
    session.commit()
    session.refresh(obj)

    return {"ok": True}
