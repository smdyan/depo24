from typing import Annotated
from fastapi import HTTPException, APIRouter
from sqlmodel import select
from src.data.init import SessionDep
from src.model.quote import Quote, QuoteCreate, QuotePublic


router = APIRouter( prefix="/quote" )


@router.post( "/", response_model=QuotePublic )
def addQuote( quote: QuoteCreate, session: SessionDep ):
    dbQuote = Quote.model_validate( quote )
    session.add( dbQuote )
    session.commit()
    session.refresh( dbQuote )
    return dbQuote


@router.delete("/{id}")
async def deleteQuote(id: int, session: SessionDep):
    quote = session.get(Quote, id)
    if not quote:
        raise HTTPException( status_code=404, detail="quote not found" )
    session.delete( quote )
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=QuotePublic)
async def getQuote(id: int, session: SessionDep):
    quote = session.get(Quote, id)
    if not quote:
        raise HTTPException(status_code=404, detail="quote not found")
    return quote
