from typing import Any
from dataclasses import dataclass
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
    operations: list["Operation"]
    last_accruel_date: date
    accrued_value: Decimal
    principal_value: Decimal
    topup_value: Decimal
    capitalized_value: Decimal
    paid_value: Decimal
    status: DepositStatus

# при прогоне функции необходимо отслеживать изменение ставки - сейчас это не реализовано
def calc_accruels(
    deposit: Deposit,
    day_count_base: int = 365,
) -> AccrualResult:    
    
    getcontext().prec = 14

    operations: list[Operation] = []
    res = AccrualResult (
        operations = operations,
        last_accruel_date = deposit.date_last_accruel,
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
    accruel_period_start = deposit.date_last_accruel + timedelta(days=1)
    # период начисления заканчивается датой перед днем фактического проведения операции или перед днем закрытия вклада
    min_date = min(date_operation, deposit.date_close)
    accruel_period_end = min_date - timedelta(days=1)                       # T

    if deposit.date_last_accruel >= accruel_period_end:
        raise AccrualAlreadyDone(f"Deposit {deposit.id} accruels already done")

    rate: Decimal = deposit.nominal_rate
    val: Decimal = _base_value(res.principal_value, res.topup_value, res.capitalized_value)
    accruel_per_day: Decimal = _calc_int_per_day(val, rate, day_count_base)

    # ежедневные начисления
    for date_accruel in _iter_days(accruel_period_start, accruel_period_end):
        res.accrued_value += accruel_per_day
        payload_accruel = _build_accruel_payload(accruel_period=date_accruel, rate=rate, base_value=val)
        
        operations.append(
            Operation(
                operation_type = DepositOperationType.INTEREST_ACCRUAL,
                business_date = date_accruel,
                operation_date = date_operation,
                amount = accruel_per_day,
                payload_json = json.dumps(payload_accruel, ensure_ascii=False),
            )
        )
        # выплата начисленных % или капитализация
        if _is_payout_next_day(date_accruel, deposit):
            date_payout = date_accruel + timedelta(days=1)

            if deposit.interest_mode == InterestModes.PAYOUT:
                operation_type = DepositOperationType.INTEREST_PAYOUT
                payload = _build_payout_payload()
                res.paid_value += res.accrued_value

            else: # interest_mode==CAPITALIZE:
                operation_type = DepositOperationType.INTEREST_CAPITALIZE
                payload = _build_payout_payload()
                res.capitalized_value += res.accrued_value
            
            operations.append(
                Operation(
                    operation_type=operation_type,
                    business_date=date_payout,
                    operation_date=date_operation,
                    amount=res.accrued_value,
                    payload_json=json.dumps(payload, ensure_ascii=False),
                )
            )
            res.accrued_value = Decimal("0")
            val = _base_value(res.principal_value, res.topup_value, res.capitalized_value)
            accruel_per_day = _calc_int_per_day(val, rate, day_count_base)

    res.last_accruel_date = accruel_period_end

    # зарытие вклада    
    if accruel_period_end == deposit.date_close - timedelta(days=1):
        payload_close = _build_close_payload(principal_val=res.principal_value, topup_val=res.topup_value, capitalized_val=res.capitalized_value)
        operations.append(
                Operation(
                    operation_type = DepositOperationType.CLOSE,
                    business_date = deposit.date_close,
                    operation_date = date_operation,
                    amount = val,
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

def _build_accruel_payload(
    *,
    accruel_period: date,
    rate: Decimal,
    base_value: Decimal,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "period": accruel_period.isoformat(),       # ISO 8601
        "rate": format(rate, "f"),                  # Decimal → string without scientific notation
        "base_value": format(base_value, "f"),      # Decimal → string
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
    period_basis = deposit.interest_period_basis
    date_open = deposit.date_open
    if deposit.interest_term==InterestTerms.MONTHLY and period_basis==PeriodAnchor.CALENDAR_MONTH:
        return (d + timedelta(days=1)).day == 1
    elif deposit.interest_term==InterestTerms.MONTHLY and deposit.interest_period_basis==PeriodAnchor.DEPOSIT_OPEN_DATE:
        payout_date = _payout_date_for_month(
            year=(d + timedelta(days=1)).year,
            month=(d + timedelta(days=1)).month,
            anchor_day=deposit.date_open.day,
        )
        return (d + timedelta(days=1)) == payout_date
    else:
        return (d + timedelta(days=1)) == deposit.date_close

def _payout_date_for_month(year: int, month: int, anchor_day: int) -> date:
    last = _last_day_of_month(date(year, month, 1))
    day = min(anchor_day, last.day)
    return date(year, month, day)
    
def _last_day_of_month(d: date) -> date:
    first_next = date(d.year, d.month, 1) + timedelta(days=32)
    first_next = date(first_next.year, first_next.month, 1)
    return first_next - timedelta(days=1)

def _base_value(principal_val, topup_val, capitalized_val) -> Decimal:
    return Decimal(principal_val + topup_val + capitalized_val)

def _calc_int_per_day(val: Decimal, r: Decimal, day_count_base: int) -> Decimal: 
    return val/Decimal(day_count_base)*r/Decimal("100")
