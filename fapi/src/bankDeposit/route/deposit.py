from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.bankDeposit.model.deposit import Deposit, DepositCreate, DepositPublicWithIncome
from src.bankDeposit.service.deposit_parameters import calc_close_date
from src.bankDeposit.service.income import calc_income_array


router = APIRouter(prefix="/deposits", tags=["deposits"])


@router.post("/")
def addDeposit(payload: DepositCreate, session: SessionDep):
    obj = Deposit(**payload.model_dump(exclude_none=True))
    
    obj.date_close = calc_close_date(obj.date_open, obj.duration)
    
    incomes = calc_income_array(obj.face_value, obj.interest_rate, obj.date_open, obj.date_close, obj.duration, payload.interest_term)
    for income in incomes:
        obj.incomes.append(income)
    
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


@router.get("/", response_model=list[DepositPublicWithIncome])    #type annotation
async def getAllDeposit(session: SessionDep):
    obj_list = session.exec(select(Deposit)).all()
    if not obj_list:
        raise HTTPException(status_code=404, detail="deposits not found")
    return obj_list


@router.get("/{id:int}", response_model=DepositPublicWithIncome)
async def getBankDeposit(id: int, session: SessionDep):
    obj = session.get( Deposit, id )
    if not obj:
        raise HTTPException(status_code=404, detail="deposit not found")
    return obj



