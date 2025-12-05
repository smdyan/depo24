from fastapi import APIRouter
from src.depositRegister.route import deposit
from src.misc.route import customer
from src.misc.route import currency
from src.misc.route import bank
from src.misc.route import import_misc
from src.ledger.route import account
from src.ledger.route import import_account


def get_router():
    router = APIRouter()
    router.include_router( deposit.router )
    router.include_router( customer.router )
    router.include_router( currency.router )
    router.include_router( bank.router )
    router.include_router( import_misc.router )
    router.include_router( account.router )
    router.include_router( import_account.router )
    return router