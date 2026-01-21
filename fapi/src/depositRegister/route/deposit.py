from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field, field_validator
from sqlmodel import select
from decimal import Decimal, InvalidOperation
from typing import List
from src.database import SessionDep
from datetime import date
from src.depositRegister.model.deposit import Deposit, DepositCreate, DepositPublicWithOps, DepositPublic
from src.depositRegister.errors import DepositError
from src.depositRegister.service.parameters import calc_close_date
from src.depositRegister.service.operation_open import get_open_operation
from src.depositRegister.service.operation_accruel import calc_accruels
from src.depositRegister.service.operation_rate import get_rate_change_operation


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


@router.post("/{id:int}/jobs-run")

async def doAccruels(id: int, session: SessionDep):
    obj = session.get( Deposit, id )
    operation_date = date.today() 
    
    try:
        result = calc_accruels(obj, operation_date)
    except DepositError as e:
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


class RateChangeRequest(BaseModel):
    effective_from: date
    new_rate: str = Field(..., description="Rate as decimal string, e.g. '12.50'")

    @field_validator("new_rate")
    @classmethod
    def validate_new_rate(cls, v: str) -> str:
        try:
            r = Decimal(v)
        except InvalidOperation:
            raise ValueError("new_rate must be a decimal string")
        if r <= 0 or r > 100:
            raise ValueError("new_rate must be in (0, 100]")
        return v


@router.post("/{id:int}/rate-change")
async def changeRate(id: int, req: RateChangeRequest, session: SessionDep):
    obj = session.get(Deposit, id)
    if not obj:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Deposit {id} not found"})

    rate = Decimal(req.new_rate)
    try:
        op = get_rate_change_operation(
            deposit=obj,
            new_rate=rate,
            effective_from_date=req.effective_from,
            operation_date=date.today(),
        )
    except DepositError as e:
        raise HTTPException(status_code=409, detail={"code": e.code, "message": str(e)})

    obj.operations.append(op)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {"ok": True}