from app.db.models.created_updated_at_document_base import CreatedUpdatedAtDocumentBase


class User(CreatedUpdatedAtDocumentBase):
    name: str
    email_id: str
    phone_numer: str
    wallet_ids: list[str]
