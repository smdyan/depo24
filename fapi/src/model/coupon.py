from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from src.model.bond import Bond

class CouponBase( SQLModel ):
    date: date
    value: int
    bondId: Optional[int] = Field( default=None, foreign_key="bond.id" )


class Coupon( CouponBase, table=True ):
    id: int = Field( default=None, primary_key=True )
    bond: Optional["Bond"] = Relationship( back_populates="coupons" )


class CouponCreate( CouponBase ):
    pass


class CouponPublic( CouponBase ):
    id: int