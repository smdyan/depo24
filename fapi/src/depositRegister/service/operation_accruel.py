from typing import Any
from dataclasses import dataclass, field
import json
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR, getcontext
from src.depositRegister.model.operation import Operation
from src.depositRegister.model.parameters import DepositOperationType, DepositStatus, InterestModes, InterestTerms, PeriodAnchor
from src.depositRegister.model.deposit import Deposit
from src.depositRegister.errors import DepositNotActive, AccrualAlreadyDone
from src.depositRegister.service.utils import to_dec


@dataclass
class AccrualResult:
    last_accrual_date: date
    accrued_value: Decimal
    principal_value: Decimal
    topup_value: Decimal
    capitalized_value: Decimal
    paid_value: Decimal
    status: DepositStatus
    operations: list[Operation] = field(default_factory=list)

# при прогоне функции необходимо отслеживать изменение ставки - сейчас это не реализовано
def calc_accruels(
    deposit: Deposit,
    day_count_base: int = 365,
) -> AccrualResult:    

    # operations: list[Operation] = []

    res = AccrualResult (
        last_accrual_date = deposit.date_last_accrual,
        accrued_value = deposit.accrued_value,
        principal_value = deposit.principal_value,
        topup_value = deposit.topup_value,
        capitalized_value = deposit.capitalized_value,
        paid_value = deposit.paid_value,
        status = deposit.status
    )

    if deposit.status != DepositStatus.ACTIVE:
        raise DepositNotActive(f"Deposit {deposit.id} is not active")

    date_operation = date.today()                                           # T+1
    accrual_period_start = deposit.date_last_accrual + timedelta(days=1)
    # период начисления заканчивается датой перед днем фактического проведения операции или перед днем закрытия вклада
    min_date = min(date_operation, deposit.date_close)
    accrual_period_end = min_date - timedelta(days=1)                       # T

    if deposit.date_last_accrual == accrual_period_end:
        raise AccrualAlreadyDone(f"Deposit {deposit.id} accruels already done")

    rate: Decimal = deposit.nominal_rate
    val: Decimal = _base_value(res.principal_value, res.topup_value, res.capitalized_value)
    accrual_per_day: Decimal = _calc_int_per_day(val, rate, day_count_base)

    # ежедневные начисления
    for date_accrual in _iter_days(accrual_period_start, accrual_period_end):
        res.accrued_value += accrual_per_day
        payload_accrual = _build_accrual_payload(rate=rate, base_value=to_dec(val), accrued_value=to_dec(res.accrued_value))
        
        res.operations.append(
            Operation(
                operation_type = DepositOperationType.INTEREST_ACCRUAL,
                business_date = date_accrual,
                operation_date = date_operation,
                amount = to_dec(accrual_per_day),
                payload_json = json.dumps(payload_accrual, ensure_ascii=False),
            )
        )
        # выплата начисленных % или капитализация
        if _is_payout_next_day(date_accrual, deposit):
            date_payout = date_accrual + timedelta(days=1)

            if deposit.interest_mode == InterestModes.PAYOUT:
                operation_type = DepositOperationType.INTEREST_PAYOUT
                payload = _build_payout_payload()
                res.paid_value += res.accrued_value

            else: # interest_mode==CAPITALIZE:
                operation_type = DepositOperationType.INTEREST_CAPITALIZE
                payload = _build_payout_payload()
                res.capitalized_value += res.accrued_value
            
            res.operations.append(
                Operation(
                    operation_type=operation_type,
                    business_date=date_payout,
                    operation_date=date_operation,
                    amount=to_dec(res.accrued_value),
                    payload_json=json.dumps(payload, ensure_ascii=False),
                )
            )
            res.accrued_value = Decimal("0")
            val = _base_value(res.principal_value, res.topup_value, res.capitalized_value)
            accrual_per_day = _calc_int_per_day(val, rate, day_count_base)

    res.last_accrual_date = accrual_period_end

    # зарытие вклада    
    if accrual_period_end == deposit.date_close - timedelta(days=1):
        payload_close = _build_close_payload(principal_val=res.principal_value, topup_val=res.topup_value, capitalized_val=to_dec(res.capitalized_value))
        res.operations.append(
                Operation(
                    operation_type = DepositOperationType.CLOSE,
                    business_date = deposit.date_close,
                    operation_date = date_operation,
                    amount = to_dec(val),
                    payload_json = json.dumps(payload_close, ensure_ascii=False),
                )
            )
        res.paid_value += val
        res.principal_value = Decimal("0")
        res.topup_value = Decimal("0")
        res.capitalized_value = Decimal("0")
        res.status = DepositStatus.CLOSED

    return res


def _build_close_payload(
    *,
    principal_val: Decimal,
    topup_val: Decimal,
    capitalized_val: Decimal,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "principal_value": format(principal_val, "f"),
        "topup_value": format(topup_val, "f"),
        "capitalized_value": format(capitalized_val, "f"),
    }
    return payload

def _build_accrual_payload(
    *,
    rate: Decimal,
    base_value: Decimal,
    accrued_value: Decimal,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "rate": format(rate, "f"),                                  # Decimal → string without scientific notation
        "base_value": format(base_value, "f"),              # Decimal → string
        "accrued_value": format(accrued_value, "f"),        # Decimal → string
    }
    return payload

def _build_payout_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "comment": "accrued value reset",
    }
    return payload

def _iter_days(start: date, end: date):
    """генератор дат начисления процентов """
    """начисление делается со следедующего дня после открытия по дату предшествующую закрытию вклада"""
    n = start
    step = timedelta(days=1)
    while n <= end:
        yield n
        n += step

def _is_payout_next_day(d: date, deposit: Deposit) -> bool:
    """True если следующий день после d — это день выплаты % (1-е число или день открытия вклада)"""
    if (d + timedelta(days=1)) == deposit.date_close:
        return True
    if deposit.interest_term==InterestTerms.MONTHLY and deposit.interest_period_basis==PeriodAnchor.CALENDAR_MONTH:
        return (d + timedelta(days=1)).day == 1
    elif deposit.interest_term==InterestTerms.MONTHLY and deposit.interest_period_basis==PeriodAnchor.DEPOSIT_DATE:
        payout_date = _payout_date_for_month(
            year=(d + timedelta(days=1)).year,
            month=(d + timedelta(days=1)).month,
            anchor_day=deposit.date_open.day,
        )
        return (d + timedelta(days=1)) == payout_date
    else:
        return False


def _payout_date_for_month(year: int, month: int, anchor_day: int) -> date:
    last = _last_day_of_month(date(year, month, 1))
    day = min(anchor_day, last.day)
    return date(year, month, day)
    
def _last_day_of_month(d: date) -> date:
    first_next = date(d.year, d.month, 1) + timedelta(days=32)
    first_next = date(first_next.year, first_next.month, 1)
    return first_next - timedelta(days=1)

def _base_value(principal_val, topup_val, capitalized_val) -> Decimal:
    return principal_val + topup_val + capitalized_val

def _calc_int_per_day(val: Decimal, r: Decimal, day_count_base: int) -> Decimal: 
    return val/Decimal(day_count_base)*r/Decimal("100")
