from datetime import datetime
from beanie import Document, Insert, Replace, Update, Save, before_event
from pydantic import Field


class CreatedUpdatedAtDocumentBase(Document):
    created_at: datetime = Field(
        description="Document created at in utc", default_factory=datetime.now
    )
    updated_at: datetime = Field(
        description="Document updated at in utc", default_factory=datetime.now
    )
    is_deleted: bool = Field(description="Is document deleted", default=False)

    @before_event(Insert, Replace, Update, Save)
    def update_time_fields(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
