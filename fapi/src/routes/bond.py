from typing import Annotated
from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.data.init import SessionDep
from src.model.bond import Bond, BondCreate, BondPublic


router = APIRouter( prefix="/bond" )


@router.post( "/", response_model=BondPublic )
def addBond( bond: BondCreate, session: SessionDep ):
    dbBond = Bond.model_validate( bond )
    session.add( dbBond )
    session.commit()
    session.refresh( dbBond )
    return dbBond


@router.delete("/{id}")
async def deleteBond(id: int, session: SessionDep):
    bond = session.get(Bond, id)
    if not bond:
        raise HTTPException(status_code=404, detail="bond not found")
    session.delete( bond )
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=BondPublic)
async def getBond(id: int, session: SessionDep):
    bond = session.get(Bond, id)
    if not bond:
        raise HTTPException(status_code=404, detail="bond not found")
    return bond
