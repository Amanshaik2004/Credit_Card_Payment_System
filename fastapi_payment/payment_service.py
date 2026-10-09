import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from .models import Card, Transaction, AuditLog
from .schemas import PaymentRequest

def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"

class PaymentService:
    @staticmethod
    def process_payment(
        db: Session,
        payment_data: PaymentRequest,
        user_id: int,
        client_ip: str = "127.0.0.1"
    ) -> Transaction:
        # Step 1: Validate card ownership and active status
        card = db.query(Card).filter(
            Card.id == payment_data.card_id,
            Card.user_id == user_id,
            Card.is_active == True
        ).first()

        if not card:
            raise ValueError("Card not found, inactive, or unauthorized.")

        # Step 2: Create initial Transaction in PENDING status (MODULE 3 Requirement)
        txn_id = generate_transaction_id()
        now = datetime.now(timezone.utc)

        transaction = Transaction(
            transaction_id=txn_id,
            user_id=user_id,
            card_id=card.id,
            amount=payment_data.amount,
            currency=payment_data.currency.upper(),
            status='PENDING',
            description=payment_data.description or "Card Payment",
            failure_reason=None,
            created_at=now,
            updated_at=now
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Step 3: Simulate Payment Gateway Processing (Success / Failure simulation)
        # Note: CVV is NEVER saved to database. It is only checked here during simulation.
        failure_reason = None
        current_year = now.year
        current_month = now.month

        # Expiry check
        if card.expiry_year < current_year or (card.expiry_year == current_year and card.expiry_month < current_month):
            failure_reason = "Card has expired"
        # Simulation triggers: CVV '000' or '999' simulates bank decline
        elif payment_data.cvv in ("000", "999"):
            failure_reason = "CVV check failed / Declined by issuing bank"
        # High amount check: amounts above 50,000 simulate bank limit exceeded
        elif payment_data.amount > Decimal("50000.00"):
            failure_reason = "Transaction amount exceeds per-transaction limit"

        # Step 4: Transition to Final Status: SUCCESS or FAILED
        if failure_reason:
            transaction.status = 'FAILED'
            transaction.failure_reason = failure_reason
            audit_action = 'PAYMENT_FAILED'
            audit_details = f"Transaction {txn_id} FAILED for user {user_id}. Reason: {failure_reason}"
        else:
            transaction.status = 'SUCCESS'
            transaction.failure_reason = None
            audit_action = 'PAYMENT_SUCCESS'
            audit_details = f"Transaction {txn_id} SUCCEEDED: charged {transaction.currency} {transaction.amount} on card ending in {card.last_4_digits}"

        transaction.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(transaction)

        # Step 5: Record Audit Log
        try:
            audit = AuditLog(
                user_id=user_id,
                action=audit_action,
                ip_address=client_ip,
                details=audit_details,
                created_at=datetime.now(timezone.utc)
            )
            db.add(audit)
            db.commit()
        except Exception:
            # Audit log failure should not break payment response
            db.rollback()

        return transaction
