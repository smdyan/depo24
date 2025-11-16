from fastapi import HTTPException, APIRouter
from pathlib import Path
from pydantic import ValidationError
from csv import DictReader
from src.database import SessionDep
from src.misc.model.customer import Customer, CustomerCreate


router = APIRouter(prefix="/import-customers", tags=["import"])

CSV_PATH = Path("/Users/lily/depo24/fapi/src/misc/asset/customers.csv") 

@router.post("/")
async def import_customerss(session: SessionDep):
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="Default CSV file not found")

    created = 0
    errors: list[dict] = []

    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = DictReader(f)

        for line_no, row in enumerate(reader, start=2):  # start=2: первая строка — заголовки
            try:
                obj_in = CustomerCreate.model_validate(row)

            except ValidationError as e:
                errors.append(
                    {
                        "line": line_no,
                        "row": row,
                        "errors": e.errors(),
                    }
                )
                continue

            obj = Customer(**obj_in.model_dump())
            session.add(obj)
            created += 1

    session.commit()
    return {
        "status": "ok",
        "created": created,
        "errors": errors,
    }

