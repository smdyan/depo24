from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

# Import all SQLModel definitions before metadata.create_all runs
from src.depositRegister.model import deposit as _deposit_model  # noqa: F401
from src.depositRegister.model import income as _income_model  # noqa: F401
from src.depositRegister.model import operation as _operation_model  # noqa: F401
from src.ledger.model import account as _ledger_account_model  # noqa: F401
from src.ledger.model import entry as _ledger_entry_model  # noqa: F401
from src.ledger.model import transaction as _ledger_transaction_model  # noqa: F401
from src.reference.model import bank as _bank_model  # noqa: F401
from src.reference.model import currency as _currency_model  # noqa: F401
from src.reference.model import customer as _customer_model  # noqa: F401


sqlite_file_name = "depo.db"
sqlite_url = f"sqlite:///./database/{sqlite_file_name}"
connect_args = {"check_same_thread": False}
# turn on alchemy 2.0 futures
engine = create_engine( sqlite_url, echo=True, future=True )


async def create_db_and_tables():
    SQLModel.metadata.create_all( engine )


def get_session():
# same as creating manualu session = Session(engine), but no need to session.close()
    with Session( engine ) as session:
        yield session


SessionDep = Annotated[ Session, Depends( get_session )]
