from pydantic.dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, ClassVar
from src.depositRegister.model.enums import InterestModes, InterestTerms

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit

Q2 = Decimal("0")

def q2(x: Decimal) -> Decimal:
    return x.quantize(Q2, rounding=ROUND_HALF_UP)

@dataclass
class AnalysisResult:
    contributed_total: Decimal
    income_realized: Decimal
    
    def __post_init__(self):
        for f in (
            "contributed_total",
            "income_realized",
        ):
            v = getattr(self, f)
            setattr(self, f, q2(v))


def get_deposit_summary(
        dep_list: list["Deposit"],
    ) -> AnalysisResult:

    contributed_val = Decimal("0")
    income_realized = Decimal("0")
    
    for dep in dep_list:
        contributed_val += dep.principal_value + dep.topup_value
        income_realized += dep.accrued_value + dep.paid_income + dep.capitalized_income
    
    res = AnalysisResult(
        contributed_total=contributed_val,
        income_realized=income_realized,
    )
    return res

