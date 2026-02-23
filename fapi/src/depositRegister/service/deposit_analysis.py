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
    contributed_value: Decimal
    balance_base: Decimal
    balance_average: Decimal
    income_realized: Decimal
    income_to_close: Decimal
    apr_realized: Decimal                                                                   # annual percentage rate at base balance (учитывает среднее значение баланса по вкладу - балансо-дни)
    irr: Decimal                                                                            # return over investment at unrecovered cost (учитывает уменьшение инвестиции при выплатах %)
    ear_current: Decimal                                                                    # effective annual rate (приведен ко вкладу сроком 1 год с выплатой в конце срока)

    
    def __post_init__(self):
        for f in (
            "contributed_value",
            "balance_base",
            "balance_average",
            "income_realized",
            "income_to_close",
            "apr_realized",
            "irr",
            "ear_current",
        ):
            v = getattr(self, f)
            setattr(self, f, q2(v))


def get_deposit_analysis(
        as_of: date,                                                                        # дата расчета анализа, должна быть больше дня открытия иначе деление на 0
        depo: "Deposit",
        
    ) -> AnalysisResult:

    CV_as_of = depo.principal_value + depo.topup_value                                      # Contributed value
    BB_as_of = depo.principal_value + depo.topup_value + depo.capitalized_income            # Base Balance - текущий баланс по вкладу (база начисления %)
    PV_as_of = BB_as_of + depo.accrued_value                                                # Position Value - стоимость позиции. MTM (mark-to-market). Для расчета IRR/XIRR.
    income_to_date = depo.accrued_value + depo.paid_income + depo.capitalized_income        # сумма всех начислений за период
    
    BDB = depo.balancedays_base                                                             # рубле-дни по текущему балансу (по базе начсления %)
    days_open = Decimal((depo.date_last_accrual - depo.date_open).days + 1)                 # точка отсчета - дата последнего начисления
    if days_open <= 0:
        BB_avg = Decimal(0)
    else:
        BB_avg = BDB / days_open                                                            # Среднее значение баланса за период с открытия
    if BDB == 0:
        apr_realized = Decimal(0)                                                           # anual percentage rate realized - фактическая процентная ставка за состоявшийся период
    else:
        apr_realized = income_to_date * Decimal("365") / BDB * Decimal("100")               # учитывает средневзвешанный рабочий баланс, и фактические начисления, а не текущую номинальную ставку
    
    
    BDС = depo.balancedays_cost                                                             # рубле-дни по невозвращенному капиталу
    if BDС == 0:
        irr_to_date = Decimal(0)                                                            # Internal Rate of Return - фактическая процентная ставка
    else:
        irr_to_date = income_to_date * Decimal("365") / BDС * Decimal("100")                # ставка c учетом выплаченых процентов


    r = depo.nominal_rate / Decimal("100")
    if depo.interest_term == InterestTerms.MONTHLY and depo.interest_mode == InterestModes.CAPITALIZE:
        n_periods = Decimal((depo.date_close - as_of).days // 30)                           # принято допущение - месяц равен 30 дням
        r_per_period = r / Decimal("12")
    else:
        n_periods = Decimal("1")
        r_per_period = r * Decimal((depo.date_close - as_of).days)/Decimal("365")
        
    income_from_date_to_close = BB_as_of * (Decimal("1") + r_per_period)**n_periods - BB_as_of    # ожидаемое поступление
    income_from_open_to_close = income_to_date + income_from_date_to_close

    """
    Вклады с ежемесячной выплатой процентов. С точки зрения вклада доходность развна вкладу с выплатой % в конце срока. Но с точки зрения бухгалтерии 
    при выплате процентов происходит уменьшение суммы вложений и от этого доходность возрастает. Первый более простой способ расчета - “Доходность на 
    средний капитал под риском”. Второй - XIRR NPV, являющийся стандартом.
    """
    if depo.interest_term == InterestTerms.END_OF_TERM:
        m = Decimal("365") / depo.duration                                                  # % periods per year (payout and capitalization)
    else:
        m = Decimal("12")                                                                   # Assumption: payouts reinvested aka capitalization
    ear = ((Decimal("1") + r/m)**m - Decimal("1")) * Decimal("100")                         # EAR - effective anual rate.  Нормализация текущей ставки по вкладу

    res = AnalysisResult(
        contributed_value=CV_as_of,
        balance_base=BB_as_of,
        balance_average= BB_avg,
        income_realized=income_to_date,
        income_to_close=income_from_open_to_close,                                           # приблизительный расчет !!!
        apr_realized=apr_realized,
        irr=irr_to_date,                                                                     # конечно, это не xirr
        ear_current=ear,
    )
    return res

