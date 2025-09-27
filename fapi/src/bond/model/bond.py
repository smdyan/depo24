from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from src.bond.model.coupon import Coupon
    from src.bond.model.quote import Quote

class BondBase( SQLModel ):
    shortName: str
    isin: str
    faceValue: int
    currencyId: str
    issDate: date
    matDate: date


class Bond( BondBase, table=True ):
    id: int = Field( default=None, primary_key=True )
    coupons: Optional[list["Coupon"]] = Relationship( back_populates="bond" )
    quotes: Optional[list["Quote"]] = Relationship( back_populates="bond" )


class BondCreate( BondBase ):
    pass

class BondPublic( BondBase ):
    id: int