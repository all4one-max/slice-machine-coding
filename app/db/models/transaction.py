from app.db.common.enums import TransactionStatus, TransactionType
from app.db.models.created_updated_at_document_base import CreatedUpdatedAtDocumentBase


class Transaction(CreatedUpdatedAtDocumentBase):
    from_wallet_id: str
    to_wallet_id: str
    amount: int
    transaction_status: TransactionStatus
