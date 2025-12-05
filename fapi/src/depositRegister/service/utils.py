from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def to_dec(x, max_digits: int = 12, decimal_places: int = 2) -> Decimal:
    """ Convert x to Decimal with fixed precision and scale.
        Enforces max total digits and decimal places."""
    try:
        d = Decimal(str(x))
    except InvalidOperation:
        raise ValueError(f"Cannot convert {x!r} to Decimal")

    # round to the desired number of decimal places
    quant = Decimal("1").scaleb(-decimal_places)  # e.g. Decimal("0.01") for 2 decimals
    d = d.quantize(quant, rounding=ROUND_HALF_UP)

    # enforce max_digits (total digits incl. integer + decimals)
    digits = len(d.as_tuple().digits)
    if digits > max_digits:
        raise ValueError(f"Value {d} exceeds max_digits={max_digits}")

    return d


