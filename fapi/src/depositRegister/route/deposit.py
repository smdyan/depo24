from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field, field_validator
from sqlmodel import select
from decimal import Decimal, InvalidOperation
from typing import List
from src.database import SessionDep
from datetime import date, timedelta
from src.depositRegister.model.deposit import Deposit, DepositCreate, DepositPublicWithOps, DepositPublic
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.parameters import DepositOperationType
from src.depositRegister.errors import DepositError
from src.depositRegister.service.parameters import calc_close_date
from src.depositRegister.service.operation_open import get_open_operation
from src.depositRegister.service.operation_accruel import calc_accruels
from src.depositRegister.service.operation_rate import get_rate_change_operation
from src.depositRegister.service.operation_topup import get_topup_operation


router = APIRouter(prefix="/deposits", tags=["deposits"])


@router.post("/")
def addDeposit(payload: DepositCreate, session: SessionDep):
    obj = Deposit(**payload.model_dump(exclude_none=True))
    
    obj.date_close = calc_close_date(obj.date_open, obj.duration)
    obj.date_last_accrual = obj.date_open
    
    operation = get_open_operation(
        obj,
        operation_date=date.today(),
    )
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


@router.post("/{id:int}/run-jobs")

async def doAccruels(id: int, session: SessionDep):
    dep = session.get( Deposit, id )
    rate_ops = session.exec(
        select(Operation)
        .where(Operation.deposit_id == dep.id)
        .where(Operation.operation_type == DepositOperationType.CHANGE_RATE)
        .where(Operation.business_date > dep.date_last_accrual)
        .order_by(Operation.business_date, Operation.operation_date)
    ).all()
    topup_ops = session.exec(
        select(Operation)
        .where(Operation.deposit_id == dep.id)
        .where(Operation.operation_type == DepositOperationType.TOPUP)
        .where(Operation.business_date > dep.date_last_accrual)
        .order_by(Operation.business_date, Operation.operation_date)
    ).all()
    operation_date = date.today() 
    
    try:
        result = calc_accruels(
            deposit=dep, 
            rate_ops=rate_ops, 
            topup_ops=topup_ops, 
            operation_date=operation_date)
    except DepositError as e:
        raise HTTPException(status_code=409, detail={"code": e.code, "message": str(e)})
    
    dep.operations.extend(result.operations)
    dep.date_last_accrual = result.last_accrual_date
    dep.accrued_value = result.accrued_value
    dep.principal_value = result.principal_value
    dep.topup_value = result.topup_value
    dep.capitalized_value = result.capitalized_value
    dep.paid_value = result.paid_value
    dep.nominal_rate = result.rate
    dep.status = result.status

    session.add(dep)
    session.commit()
    session.refresh(dep)
    return {"ok": True}


class OperationRequest(BaseModel):
    effective_from: date
    value: str = Field(..., description="Value as decimal string, e.g. '12.50'")

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        try:
            r = Decimal(v)
        except InvalidOperation:
            raise ValueError("value must be a decimal string")
        return v


@router.post("/{id:int}/change-rate")
async def changeRate(id: int, req: OperationRequest, session: SessionDep):
    obj = session.get(Deposit, id)
    if not obj:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Deposit {id} not found"})

    try:
        op = get_rate_change_operation(
            deposit=obj,
            new_rate=Decimal(req.value),
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


@router.post("/{id:int}/topup-depo")
async def topup(id: int, req: OperationRequest, session: SessionDep):
    obj = session.get(Deposit, id)
    if not obj:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Deposit {id} not found"})

    try:
        op = get_topup_operation(
            deposit=obj,
            topup_value=Decimal(req.value),
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