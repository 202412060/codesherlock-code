"""Refund summary lines for the monthly statement."""
from decimal import Decimal

from statement_export import _format_amount, compute_total


def refund_summary(refunds: list) -> str:
    """One line with the refund count and total."""
    total = compute_total(refunds)
    return f"{len(refunds)} refunds, total {_format_amount(Decimal(total))}"
