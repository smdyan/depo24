from typing import Any, Optional
from dataclasses import dataclass, field
import json
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
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
    rate: Decimal
    status: DepositStatus
    operations: list[Operation] = field(default_factory=list)


def calc_accruels(
    deposit: Deposit,
    rate_ops: list[Operation],
    operation_date: date,
    day_count_base: int = 365,
) -> AccrualResult:    

    res = AccrualResult (
        last_accrual_date = deposit.date_last_accrual,
        accrued_value = deposit.accrued_value,
        principal_value = deposit.principal_value,
        topup_value = deposit.topup_value,
        capitalized_value = deposit.capitalized_value,
        paid_value = deposit.paid_value,
        rate=deposit.nominal_rate,
        status = deposit.status
    )

    if deposit.status != DepositStatus.ACTIVE:
        raise DepositNotActive(f"Deposit {deposit.id} is not active")

    accrual_period_start = deposit.date_last_accrual + timedelta(days=1)
    # период начисления заканчивается датой перед днем фактического проведения операции или перед днем закрытия вклада
    min_date = min(operation_date, deposit.date_close)
    accrual_period_end = min_date - timedelta(days=1)

    if deposit.date_last_accrual >= accrual_period_end:
        raise AccrualAlreadyDone(f"Deposit {deposit.id} accruels already done")

    pending_rate_ops = _get_pending_rate_ops(list(rate_ops), accrual_period_start)             # создает shallow-копию списка
    pending_rate_ops.sort(key=lambda op: (_effective_from(op), op.operation_date))
    next_rate_op = pending_rate_ops.pop(0) if pending_rate_ops else None
    
    val: Decimal = _base_value(res.principal_value, res.topup_value, res.capitalized_value)
    accrual_per_day: Decimal

    # ежедневные начисления
    for date_accrual in _iter_days(accrual_period_start, accrual_period_end):
        # проверка актуальной ставки
        while next_rate_op is not None and date_accrual >= _effective_from(next_rate_op):
            res.rate = _rate_from_op(next_rate_op)
            next_rate_op = pending_rate_ops.pop(0) if pending_rate_ops else None

        accrual_per_day = _calc_int_per_day(val, res.rate, day_count_base)          # каждый день считать накладно, но ладно
        res.accrued_value += accrual_per_day
        payload_accrual = _build_accrual_payload(rate=res.rate, base_value=to_dec(val), accrued_value=to_dec(res.accrued_value))
        
        res.operations.append(
            Operation(
                operation_type = DepositOperationType.INTEREST_ACCRUAL,
                business_date = date_accrual,
                operation_date = operation_date,
                amount = to_dec(accrual_per_day),
                payload_json = json.dumps(payload_accrual, ensure_ascii=False),
            )
        )
        # выплата начисленных % и капитализация
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
                    operation_date=operation_date,
                    amount=to_dec(res.accrued_value),
                    payload_json=json.dumps(payload, ensure_ascii=False),
                )
            )
            res.accrued_value = Decimal("0")
            val = _base_value(res.principal_value, res.topup_value, res.capitalized_value)

    res.last_accrual_date = accrual_period_end

    # зарытие вклада    
    if accrual_period_end == deposit.date_close - timedelta(days=1):
        payload_close = _build_close_payload(principal_val=res.principal_value, topup_val=res.topup_value, capitalized_val=to_dec(res.capitalized_value))
        res.operations.append(
                Operation(
                    operation_type = DepositOperationType.CLOSE,
                    business_date = deposit.date_close,
                    operation_date = operation_date,
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
        "rate": format(rate, "f"),
        "base_value": format(base_value, "f"),
        "accrued_value": format(accrued_value, "f"),
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


def _get_pending_rate_ops(rate_ops: list[Operation], min_effective_from: date) -> list[Operation]:
    """Оставляет только операции изменения ставки, у которых payload.effective_from >= accrual_period_start."""
    def keep(op: Operation) -> bool:
        if not op.payload_json:
            return False

        try:
            payload: dict[str, Any] = json.loads(op.payload_json)
        except (TypeError, json.JSONDecodeError):
            return False

        eff_s = payload.get("effective_from")
        if not eff_s:
            return False

        try:
            eff_d = date.fromisoformat(eff_s)  # "YYYY-MM-DD"
        except ValueError:
            return False

        return eff_d >= min_effective_from

    rate_ops[:] = [op for op in rate_ops if keep(op)]
    return rate_ops


def _rate_from_op(op: Operation) -> Decimal:
    if not op.payload_json:
        raise ValueError("RATE_CHANGE op has empty payload_json")

    payload: dict[str, Any] = json.loads(op.payload_json)
    rate_s = payload.get("rate")
    if rate_s is None or rate_s == "":
        raise ValueError("RATE_CHANGE op payload has no 'rate'")

    try:
        return Decimal(str(rate_s))
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"RATE_CHANGE op payload has invalid rate: {rate_s!r}") from e

def _effective_from(op: Operation) -> date:
    if not op.payload_json:
        raise ValueError("RATE_CHANGE op has empty payload_json")

    payload: dict[str, Any] = json.loads(op.payload_json)
    eff_s = payload.get("effective_from")
    if not eff_s:
        raise ValueError("RATE_CHANGE op payload has no 'effective_from'")

    return date.fromisoformat(eff_s)
