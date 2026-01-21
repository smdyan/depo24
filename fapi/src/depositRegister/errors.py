class DepositError(Exception):
    """Base class for all accrual domain errors"""
    code = "ACCRUAL_ERROR"


class DepositNotActive(DepositError):
    code = "DEPOSIT_NOT_ACTIVE"


class AccrualAlreadyDone(DepositError):
    code = "ACCRUAL_ALREADY_DONE"


class InvalidAccrualPeriod(DepositError):
    code = "INVALID_ACCRUAL_PERIOD"


class WrongDate(DepositError):
    code = "DATE_MARGINS_INVALIDATE"
