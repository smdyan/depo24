from fastapi import HTTPException, APIRouter
from pathlib import Path
from pydantic import ValidationError
from sqlmodel import select
from csv import DictReader
from src.database import SessionDep
from src.ledger.model.account import Account, AccountCreate


router = APIRouter(prefix="/import-chart", tags=["import"])

CHART_CSV_PATH = Path("/Users/lily/depo24/fapi/src/ledger/assets/account_chart.csv") 


async def import_from_csv(path: Path, create_model, db_model, session: SessionDep):
    
    if not path.exists():
        raise HTTPException(status_code=404, detail="Default CSV file not found")

    created = 0
    errors: list[dict] = []

    with path.open("r", encoding="utf-8") as f:
        reader = DictReader(f)

        for line_no, row in enumerate(reader, start=2):  # start=2: первая строка — заголовки
            try:
                payload = create_model.model_validate(row)

            except ValidationError as e:
                errors.append(
                    {
                        "line": line_no,
                        "row": row,
                        "errors": e.errors(),
                    }
                )
                continue

            obj = db_model(**payload.model_dump(exclude={"parent_name"}))

            # обработка parent_name, если он есть в модели
            parent_name = getattr(payload, "parent_name", None)

            if parent_name:
                parent_obj = session.exec(
                    select(db_model).where(db_model.name == parent_name)
                ).first()

                if not parent_obj:
                    errors.append(
                        {
                            "line": line_no,
                            "row": row,
                            "errors": [
                                {
                                    "loc": ["parent_name"],
                                    "msg": f"parent account with name '{parent_name}' not found",
                                    "type": "value_error.parent_not_found",
                                }
                            ],
                        }
                    )
                    continue  # пропускаем эту строку, не создаём объект

                obj.parent_id = parent_obj.id

            session.add(obj)
            created += 1

    return created, errors

@router.post("/")
async def import_misc(session: SessionDep):
    account_created, account_errors = await import_from_csv(
        path=CHART_CSV_PATH,
        create_model=AccountCreate,
        db_model=Account,
        session=session,
    )

    session.commit()
    return {
        "status": "ok",
        "accounts": {
            "created": account_created,
            "errors": account_errors,
        },
    }