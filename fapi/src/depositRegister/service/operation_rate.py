from typing import Any
import json
from datetime import date
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.enums import DepositOperationType
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.service.utils import to_dec
from src.depositRegister.errors import WrongDate


def get_rate_change_operation(
    deposit: Deposit,
    new_rate: Decimal,
    effective_from_date: date,
    operation_date: date,
) -> Operation:
    
    if effective_from_date >= deposit.date_close:
        raise WrongDate(f"Effective date wrong, behinde deposit close date")
    
    if effective_from_date <= deposit.date_last_accrual:
        raise WrongDate(f"Effective date wrong, accruals already done for this date")

    payload = build_rate_change_payload()

    op = Operation(
        operation_type=DepositOperationType.CHANGE_RATE,
        business_date=effective_from_date,
        operation_date=operation_date,
        amount=to_dec(new_rate),
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    return op


def build_rate_change_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "comment": str("Operation.amount contains Deposit.rate"),
        "reason": str("by user"),
    }
    return payload

