from typing import Annotated
from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.database import SessionDep
from src.model.coupon import Coupon, CouponCreate, CouponPublic


router = APIRouter( prefix="/coupon" )


@router.post( "/", response_model=CouponPublic )
def addCoupon( coupon: CouponCreate, session: SessionDep ):
    dbCoupon = Coupon.model_validate( coupon )
    session.add( dbCoupon )
    session.commit()
    session.refresh( dbCoupon )
    return dbCoupon


@router.delete("/{id}")
async def deleteCoupon(id: int, session: SessionDep):
    coupon = session.get(Coupon, id)
    if not coupon:
        raise HTTPException(status_code=404, detail="coupon not found")
    session.delete( coupon )
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=CouponPublic)
async def getCoupon(id: int, session: SessionDep):
    coupon = session.get(Coupon, id)
    if not coupon:
        raise HTTPException(status_code=404, detail="coupon not found")
    return coupon
