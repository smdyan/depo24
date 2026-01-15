from typing import Any
from dataclasses import dataclass
import json
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.parameters import DepositOperationType, DepositStatus
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.errors import DepositNotActive, AccrualAlreadyDone

from src.depositRegister.service.utils import to_dec


@dataclass
class AccrualResult:
    operations: list["Operation"]
    last_accrual_date: date
    accrued_value: Decimal


def calc_accruels(
    deposit: Deposit,
    day_count_base: int = 365,
) -> AccrualResult:
    
    date_last_accruel = deposit.date_last_accruel
    date_operation = date.today()                                       # T+1
    accruel_period_start = date_last_accruel + timedelta(days=1)
    accruel_period_end = date_operation - timedelta(days=1)             # T

    if deposit.status != DepositStatus.ACTIVE:
        raise DepositNotActive(f"Deposit {deposit.id} is not active")
    
    if date_last_accruel >= accruel_period_end:
        raise AccrualAlreadyDone(f"Deposit {deposit.id} accruels already done")

    operations: list[Operation] = []
    r = deposit.nominal_rate
    val = deposit.principal_value + deposit.topup_value + deposit.capitalized_value
    accruel_per_day = val/day_count_base*r/100
    accrued_sum = 0

    for date_accruel in _iter_days(accruel_period_start, accruel_period_end):
        accrued_sum += accruel_per_day
        payload = build_accruel_payload(accruel_period=date_accruel, rate=r, base_value=val)
        op = Operation(
            operation_type=DepositOperationType.INTEREST_ACCRUAL,
            business_date=date_operation,
            amount=accruel_per_day,
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        operations.append(op)
    
    date_last_accruel = accruel_period_end
    accrued_value = deposit.accrued_value + accrued_sum
    ret = AccrualResult(operations, date_last_accruel, accrued_value)
    return ret


def build_accruel_payload(
    *,
    accruel_period: date,
    rate: Decimal,
    base_value: Decimal,
) -> dict[str, Any]:
    
    payload: dict[str, Any] = {
        "period": accruel_period.isoformat(),   # ISO 8601
        "rate": format(rate, "f"),               # Decimal → string without scientific notation
        "base_value": format(base_value, "f"),   # Decimal → string
    }
    return payload


def _iter_days(start: date, end: date):
    """генератор дат начисления процентов со следедующего дня после открытия и заканчивая днем предшествующим дате операции или закрытия вклада"""
    n = start
    step = timedelta(days=1)

    while n < end:
        n += step
        yield n
        