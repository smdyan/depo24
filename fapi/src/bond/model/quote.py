from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from src.bond.model.bond import Bond

class QuoteBase( SQLModel ):
    date: date
    price: int
    closePrice: Optional[int]
    minPrice: Optional[int]
    maxPrice: Optional[int]
    bondId: Optional[int] = Field( default=None, foreign_key="bond.id" )


class Quote( QuoteBase, table=True ):
    id: int = Field( default=None, primary_key=True )
    bond: Optional["Bond"] = Relationship( back_populates="quotes" )


class QuoteCreate( QuoteBase ):
    pass


class QuotePublic( QuoteBase ):
    id: int