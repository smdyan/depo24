from typing import Any
import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.enums import DepositOperationType
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.service.utils import to_dec
from src.depositRegister.service.deposit_parameters import calc_close_date


@dataclass
class OpenResult:
    date_close: date
    date_last_accrual: date
    balancedays_base: Decimal
    balancedays_exposure: Decimal
    operation: Operation


def open_deposit(
    *,
    deposit: Deposit,
    operation_date: date,
) -> OpenResult:
    
    date_close = calc_close_date(deposit.date_open, deposit.duration)
    date_last_accrual = deposit.date_open - timedelta(days=1)

    payload = build_open_payload(initial_rate=deposit.nominal_rate, effective_from=deposit.date_open)

    op = Operation(
        operation_type=DepositOperationType.OPEN,
        business_date=deposit.date_open,
        operation_date=operation_date,
        amount=to_dec(deposit.principal_value),
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
   
    res = OpenResult(
        date_close = date_close,
        date_last_accrual = date_last_accrual,
        balancedays_base = 0,
        balancedays_exposure = 0,
        operation = op,
    )

    return res


def build_open_payload(
    *,
    initial_rate: Decimal,
    effective_from: date,
) -> dict[str, Any]:
    
    payload: dict[str, Any] = {
        "rate": format(initial_rate, ".2f"),
        "effective_from": effective_from.isoformat(),
        "reason": "initial",
    }
    return payload

