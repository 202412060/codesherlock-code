"""Shared money conversion used across the ledger reports."""
from decimal import Decimal, ROUND_HALF_UP


def to_cents(amount) -> int:
    """Convert a decimal amount to whole cents, rounding half up."""
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
