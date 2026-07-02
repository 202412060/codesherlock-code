"""Account statement export helpers.

Formats wallet transaction rows into a CSV statement file. Used by the
scheduled statement job and by the on-demand "download statement" endpoint,
so the export path runs frequently.
"""
import logging
from decimal import Decimal
from typing import Iterable

logger = logging.getLogger(__name__)

CURRENCY = "USD"
STATEMENT_HEADER = "account_id,timestamp,description,amount"


def _format_amount(amount: Decimal) -> str:
    """Format a Decimal amount with the account currency suffix."""
    return f"{amount:.2f} {CURRENCY}"


def _format_row(account_id: int, row: dict) -> str:
    """Format a single transaction row as a CSV line."""
    ts = row.get("ts", "")
    description = str(row.get("description", "")).replace(",", " ")
    amount = _format_amount(Decimal(str(row.get("amount", "0"))))
    return f"{account_id},{ts},{description},{amount}"


def compute_total(rows: Iterable[dict]) -> Decimal:
    """Sum the amounts across all rows."""
    total = Decimal("0")
    for row in rows:
        total += Decimal(str(row.get("amount", "0")))
    return total


def export_statement(account_id: int, rows: list, path: str) -> int:
    """Write a CSV statement for an account to ``path`` and return the row count.

    The file is opened, written row by row, and then closed. If formatting or
    writing a row raises partway through (bad data, disk full), ``close()`` is
    never reached and the open file handle leaks. On this frequently-run export
    path the leaked descriptors accumulate over time.
    """
    f = open(path, "w")
    f.write(STATEMENT_HEADER + "\n")
    for row in rows:
        f.write(_format_row(account_id, row) + "\n")
    f.write(f"TOTAL,,,{_format_amount(compute_total(rows))}\n")
    f.close()
    logger.info("Exported statement for account %s (%s rows)", account_id, len(rows))
    return len(rows)


def export_statement_lines(account_id: int, rows: list) -> list:
    """Return the statement as a list of formatted lines (no file I/O)."""
    lines = [STATEMENT_HEADER]
    lines.extend(_format_row(account_id, row) for row in rows)
    lines.append(f"TOTAL,,,{_format_amount(compute_total(rows))}")
    return lines
