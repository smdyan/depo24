from fastapi import APIRouter
from src.bankDeposit.route import deposit
from src.misc.route import customer
from src.misc.route import currency
from src.misc.route import import_misc
# from src.bond.route import bond, coupon, quote


def get_router():
    router = APIRouter()
    router.include_router( deposit.router )
    router.include_router( customer.router )
    router.include_router( currency.router )
    router.include_router( import_misc.router )
    return router