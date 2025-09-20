from fastapi import APIRouter
from src.routes import bond, coupon, quote, bankDeposit


def get_router():
    router = APIRouter()
    router.include_router( bond.router )
    router.include_router( coupon.router )
    router.include_router( quote.router )
    router.include_router( bankDeposit.router )
    return router