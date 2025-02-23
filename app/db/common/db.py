import asyncio
import logging
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import DATABASE_NAME, MONGODB_URL
from app.db.common.db_models import DOCUMENT_MODELS

logger = logging.getLogger(__name__)


async def setup_db() -> None:
    mongodb_url = MONGODB_URL
    client = AsyncIOMotorClient(mongodb_url)
    client.get_io_loop = asyncio.get_event_loop  # type:ignore
    database = client.get_database(DATABASE_NAME)
    await init_beanie(
        database=database,
        document_models=DOCUMENT_MODELS,  # type: ignore
        allow_index_dropping=True,
    )
