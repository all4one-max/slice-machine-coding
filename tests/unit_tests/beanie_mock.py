import unittest
from unittest.mock import patch, AsyncMock
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from app.db.common.db_models import DOCUMENT_MODELS


class MockBaseDB(unittest.IsolatedAsyncioTestCase):
    async def init_mock_db(self) -> AsyncMongoMockClient:
        async_client = AsyncMongoMockClient()
        await init_beanie(
            document_models=DOCUMENT_MODELS,  # type: ignore
            database=async_client.get_database(name="unit_test_db"),
        )

        return async_client

    # asyncSetUp method will be executed before each test method
    async def asyncSetUp(self) -> None:
        self.client = await self.init_mock_db()

        # Mocking Beanie's save method
        self.mock_beanie_save = patch("beanie.Document.save", new_callable=AsyncMock)
        self.mock_save = self.mock_beanie_save.start()

    # asyncTearDown method will be executed after each test method
    async def asyncTearDown(self) -> None:
        # Clean up or release resources if needed
        self.client.close()
        self.mock_beanie_save.stop()
