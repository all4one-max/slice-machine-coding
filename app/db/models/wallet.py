from dataclasses import Field
from beanie import Link
from app.db.models.created_updated_at_document_base import CreatedUpdatedAtDocumentBase
from app.db.models.user import User


class Wallet(CreatedUpdatedAtDocumentBase):
    user_id: str
    max_balance: int
    cur_balance: int
