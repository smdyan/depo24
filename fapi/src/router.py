from fastapi import APIRouter
from src.bankDeposit.route import deposit
from src.bond.route import bond, coupon, quote


def get_router():
    router = APIRouter()
    router.include_router( bond.router )
    router.include_router( coupon.router )
    router.include_router( quote.router )
    router.include_router( deposit.router )
    return router