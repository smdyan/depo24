from fastapi import APIRouter
from src.depositRegister.route import deposit
from src.reference.route import customer
from src.reference.route import currency
from src.reference.route import bank
from src.reference.route import import_refs
from src.ledger.route import account
from src.ledger.route import import_account


def get_router():
    router = APIRouter()
    router.include_router( deposit.router )
    router.include_router( customer.router )
    router.include_router( currency.router )
    router.include_router( bank.router )
    router.include_router( import_refs.router )
    router.include_router( account.router )
    router.include_router( import_account.router )
    return router