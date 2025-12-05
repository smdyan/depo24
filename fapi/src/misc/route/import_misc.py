from fastapi import HTTPException, APIRouter
from pathlib import Path
from pydantic import ValidationError
from csv import DictReader
from src.database import SessionDep
from src.misc.model.customer import Customer, CustomerCreate
from src.misc.model.currency import Currency, CurrencyCreate
from src.misc.model.bank import Bank, BankCreate


router = APIRouter(prefix="/import-misc", tags=["import"])

CUSTOMER_CSV_PATH = Path("/Users/lily/depo24/fapi/src/misc/assets/customers.csv") 
CURRENCY_CSV_PATH = Path("/Users/lily/depo24/fapi/src/misc/assets/currencies.csv") 
BANK_CSV_PATH = Path("/Users/lily/depo24/fapi/src/misc/assets/banks.csv") 


async def import_from_csv(path: Path, create_model, db_model, session: SessionDep):
    
    if not path.exists():
        raise HTTPException(status_code=404, detail="Default CSV file not found")

    created = 0
    errors: list[dict] = []

    with path.open("r", encoding="utf-8") as f:
        reader = DictReader(f)

        for line_no, row in enumerate(reader, start=2):  # start=2: первая строка — заголовки
            try:
                obj_in = create_model.model_validate(row)

            except ValidationError as e:
                errors.append(
                    {
                        "line": line_no,
                        "row": row,
                        "errors": e.errors(),
                    }
                )
                continue

            obj = db_model(**obj_in.model_dump())
            session.add(obj)
            created += 1

    return created, errors

@router.post("/")
async def import_misc(session: SessionDep):
    customer_created, customer_errors = await import_from_csv(
        path=CUSTOMER_CSV_PATH,
        create_model=CustomerCreate,
        db_model=Customer,
        session=session,
    )

    currency_created, currency_errors = await import_from_csv(
        path=CURRENCY_CSV_PATH,
        create_model=CurrencyCreate,
        db_model=Currency,
        session=session,
    )

    bank_created, bank_errors = await import_from_csv(
        path=BANK_CSV_PATH,
        create_model=BankCreate,
        db_model=Bank,
        session=session,
    )

    session.commit()
    return {
        "status": "ok",
        "customers": {
            "created": customer_created,
            "errors": customer_errors,
        },
        "currency": {
            "created": currency_created,
            "errors": currency_errors,
        },
        "bank": {
            "created": bank_created,
            "errors": bank_errors,
        },
    }