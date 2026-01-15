class AccrualError(Exception):
    """Base class for all accrual domain errors"""
    code = "ACCRUAL_ERROR"


class DepositNotActive(AccrualError):
    code = "DEPOSIT_NOT_ACTIVE"


class AccrualAlreadyDone(AccrualError):
    code = "ACCRUAL_ALREADY_DONE"


class InvalidAccrualPeriod(AccrualError):
    code = "INVALID_ACCRUAL_PERIOD"
