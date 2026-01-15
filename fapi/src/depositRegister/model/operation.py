from sqlmodel import SQLModel, Relationship, Field as SQLField
from sqlalchemy import Column, Numeric
from decimal import Decimal
from typing import Any, Optional, TYPE_CHECKING
from datetime import date
import json
from pydantic import field_validator
from src.depositRegister.model.parameters import DepositOperationType

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit


class OperationBase(SQLModel):
    deposit_id: int | None = SQLField(default=None, foreign_key="deposit.id")       # "deposit" is the default name of the table in the database
    operation_type: DepositOperationType
    business_date: date
    amount: Decimal = SQLField(sa_column=Column(Numeric(12, 2)), default=Decimal("0.00"))
    payload_json: str | None = SQLField(default=None)


class Operation(OperationBase, table=True):
    id: int = SQLField(default=None, primary_key=True)
    deposit: Optional["Deposit"] = Relationship(back_populates="operations")


class OperationPublic(OperationBase):
    id: int
    payload_json: dict[str, Any] | None = None

    @field_validator("payload_json", mode="before")
    @classmethod
    def parse_payload_json(cls, value: Any) -> Any:
        if value is None or isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return value
        return value


class OperationCreate(OperationBase):
    pass
