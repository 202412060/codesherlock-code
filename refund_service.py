"""Refund rules for customer orders."""


class RefundService:
    """Decides and records refunds — ⚠ limits are per order."""

    max_refund = 500

    def __init__(self, ledger):
        self.ledger = ledger

    def issue_refund(self, order_id, amount):
        if amount <= 0 or amount > self.max_refund:
            return False
        self.ledger.append({"order_id": order_id, "amount": -amount})
        return True

    def total_refunded(self):
        return -sum(entry["amount"] for entry in self.ledger)

    @staticmethod
    def currency():
        return "USD"


def build_service():
    return RefundService(ledger=[])
