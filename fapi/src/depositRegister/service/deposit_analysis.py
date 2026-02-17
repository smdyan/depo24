from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, ClassVar
from src.depositRegister.model.enums import InterestModes, InterestTerms, DepositOperationType, DepositStatus

if TYPE_CHECKING:
    from src.depositRegister.model.deposit import Deposit

Q2 = Decimal("0.01")

def q2(x: Decimal) -> Decimal:
    return x.quantize(Q2, rounding=ROUND_HALF_UP)

@dataclass
class AnalysisResult:
    balance_base: Decimal
    balance_exposure: Decimal
    balance_average: Decimal
    anual_rate_base: Decimal
    anual_rate_invest: Decimal
    income_to_date: Decimal
    income_to_close: Decimal
    product_ear: Decimal

    
    def __post_init__(self):
        for f in (
            "balance_base",
            "balance_exposure",
            "balance_average",
            "anual_rate_base",
            "anual_rate_invest",
            "income_to_date",
            "income_to_close",
            "product_ear",
        ):
            v = getattr(self, f)
            setattr(self, f, q2(v))


def get_deposit_analysis(
        as_of: date,                                                                        # дата расчета анализа, должна быть больше дня открытия иначе деление на 0
        depo: "Deposit",
        
    ) -> AnalysisResult:

    BB_as_of = depo.principal_value + depo.topup_value + depo.capitalized_income             # Base Balance - текущий баланс по вкладу (база начисления %)
    PV_as_of = BB_as_of + depo.accrued_value                                                # Position Value - стоимость позиции. MTM (mark-to-market). Для расчета IRR/XIRR.

    income_to_date = depo.accrued_value + depo.paid_income + depo.capitalized_income          # сумма всех начислений за период

    BDB = depo.balancedays_base                                                             # рубле-дни по текущему балансу (по базе начсления %)
    if BDB == 0:
        apr_to_date_base = Decimal(0)
    else:
        apr_to_date_base = income_to_date * Decimal("365") / BDB * Decimal("100")           # ставка по начислениям за состоявшийся период по рабочему балансу, приведенная к году (APR)
    
    if depo.status == DepositStatus.ACTIVE:
        BE_as_of = depo.principal_value + depo.topup_value - depo.paid_income               # Exposure - net_invested инвестированная сумма (). “cash yield на капитал под риском”
    else:
        BE_as_of = depo.principal_value + depo.topup_value                                  # остаток 0. Проверка, что все деньги выведены
    
    BDE = depo.balancedays_exposure                                                         # рубле-дни по вложениям (по экспозиции)
    if BDE == 0:
        apr_to_date_exposure = Decimal(0)
    else:
        apr_to_date_exposure = income_to_date * Decimal("365") / BDE * Decimal("100")       # ставка по начислениям за состоявшийся период по "вложениям под риском", приведенная к году (APR)

    days_open = Decimal((depo.date_last_accrual - depo.date_open).days + 1)                 # точка отсчета - дата последнего начисления
    if days_open <= 0:
        BB_avg = Decimal(0)
    else:
        BB_avg = BDB / days_open                                                                # Среднее значение баланса за период с открытия


    r = depo.nominal_rate / Decimal("100")
    if depo.interest_term == InterestTerms.MONTHLY and depo.interest_mode == InterestModes.CAPITALIZE:
        n_periods = Decimal((depo.date_close - as_of).days // 30)                           # принято допущение - месяц равен 30 дням
        r_per_period = r / Decimal("12")
    else:
        n_periods = Decimal("1")
        r_per_period = r * Decimal((depo.date_close - as_of).days)/Decimal("365")
        
    income_from_date_to_close = BB_as_of * (Decimal("1") + r_per_period)**n_periods - BB_as_of    # ожидаемое поступление, без учета режима и периодичности процентов
    income_from_open_to_close = income_to_date + income_from_date_to_close

    """
    Вклады с ежемесячной выплатой процентов. С точки зрения вклада доходность развна вкладу с выплатой % в конце срока. Но с точки зрения бухгалтерии 
    при выплате процентов происходит уменьшение суммы вложений и от этого доходность возрастает. Первый более простой способ расчета - “Доходность на 
    средний капитал под риском”. Второй - XIRR NPV, являющийся стандартом.
    """
    if depo.interest_term == InterestTerms.END_OF_TERM:
        m = Decimal("365") / depo.duration                                                  # % periods per year (payout and capitalization)
    else:
        m = Decimal("12")
    effective_anual_rate = ((Decimal("1") + r/m)**m - Decimal("1")) * Decimal("100")        # Assumption, payouts reinvested at same rate aka capitalization

    res = AnalysisResult(
        balance_base=BB_as_of,
        balance_exposure=BE_as_of,
        balance_average= BB_avg,
        anual_rate_base=apr_to_date_base,
        anual_rate_invest=apr_to_date_exposure,
        income_to_date=income_to_date,
        income_to_close=income_from_open_to_close,
        product_ear=effective_anual_rate,
    )
    return res

