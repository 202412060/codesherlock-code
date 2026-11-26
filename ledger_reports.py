"""Ledger report totals, one function per entry type. All amounts are returned in cents."""
from ledger_helpers import to_cents


def total_deposits(entries: list) -> int:
    """Total of deposits entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "deposits")


def total_withdrawals(entries: list) -> int:
    """Total of withdrawals entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "withdrawals")


def total_fees(entries: list) -> int:
    """Total of fees entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "fees")


def total_refunds(entries: list) -> int:
    """Total of refunds entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "refunds")


def total_chargebacks(entries: list) -> int:
    """Total of chargebacks entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "chargebacks")


def total_interest(entries: list) -> int:
    """Total of interest entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "interest")


def total_transfers_in(entries: list) -> int:
    """Total of transfers in entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "transfers_in")


def total_transfers_out(entries: list) -> int:
    """Total of transfers out entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "transfers_out")


def total_adjustments(entries: list) -> int:
    """Total of adjustments entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "adjustments")


def total_rewards(entries: list) -> int:
    """Total of rewards entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "rewards")


def total_holds(entries: list) -> int:
    """Total of holds entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "holds")


def total_reversals(entries: list) -> int:
    """Total of reversals entries, in cents."""
    return sum(to_cents(e["amount"]) for e in entries if e.get("type") == "reversals")
