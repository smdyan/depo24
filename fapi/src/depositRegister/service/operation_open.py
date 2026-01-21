from typing import Any
import json
from datetime import date
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.parameters import DepositOperationType
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.service.utils import to_dec


def get_open_operation(
    deposit: Deposit,
) -> Operation:
    
    op_date = date.today()
    payload = build_open_rate_payload(initial_rate=deposit.nominal_rate, effective_from=deposit.date_open)

    op = Operation(
        operation_type=DepositOperationType.OPEN,
        business_date=deposit.date_open,
        operation_date=op_date,
        amount=deposit.principal_value,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    return op


def build_open_rate_payload(
    *,
    initial_rate: Decimal,
    effective_from: date,
) -> dict[str, Any]:
    
    payload: dict[str, Any] = {
        "rate": str(initial_rate),
        "effective_from": effective_from.isoformat(),                   # возможно запланированное изменение в дату отличную от даты операции
        "reason": str("initial"),
    }
    return payload

