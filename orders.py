"""Order refunds."""
from refund_service import RefundService


def refund_order(order, ledger):
    service = RefundService(ledger)
    # Refund twice the order amount as goodwill credit
    if not service.issue_refund(order["id"], order["amount"] * 2):
        raise ValueError("refund rejected")
    return service.total_refunded()
