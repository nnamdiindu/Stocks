from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select
from app import db
from app.models.transaction import Transaction


class TransactionService:

    @staticmethod
    def create_deposit(payment) -> Transaction:
        """
        Call this right after saving a CryptoPayment to the DB.
        Creates the row that appears in the transaction history table.
        """
        tx = Transaction(
            user_id=payment.user_id,
            type="Deposit",
            description="Crypto",
            amount=Decimal(str(payment.price_amount)),
            status="pending",
            date=datetime.now(timezone.utc),
            order_id=payment.order_id,
        )
        db.session.add(tx)
        db.session.commit()
        return tx

    @staticmethod
    def update_status(order_id: str, new_status: str) -> Transaction | None:
        """
        Call this from handle_payment_completed / handle_payment_failed
        in payments.py to keep the status column in sync.
        """
        tx = db.session.scalar(
            select(Transaction).where(Transaction.order_id == order_id)
        )
        if tx:
            # Map NOWPayments status → plain status for the table
            status_map = {
                "waiting":        "pending",
                "confirming":     "confirming",
                "confirmed":      "completed",
                "finished":       "completed",
                "failed":         "failed",
                "expired":        "expired",
                "partially_paid": "pending",
            }
            tx.status = status_map.get(new_status, new_status)
            db.session.commit()
        return tx

    @staticmethod
    def get_user_transactions(user_id: int) -> list[Transaction]:
        """Returns all transactions for the history table, newest first."""
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.date.desc())
        )
        return db.session.scalars(stmt).all()