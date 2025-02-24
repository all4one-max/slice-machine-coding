from unittest.mock import AsyncMock, patch
from app.utils.exception import RandomException
from app.utils.util import random_function
from tests.unit_tests.beanie_mock import MockBaseDB


class TestRandomFunction(MockBaseDB):
    @patch("app.utils.util.random_function2", new_callable=AsyncMock)
    async def test_random_func_value_more_than_5(
        self, mock_random_function2: AsyncMock
    ) -> None:
        mock_random_function2.return_value = 6
        val = await random_function()
        self.assertEqual(val, True)

    @patch("app.utils.util.random_function2", new_callable=AsyncMock)
    async def test_random_func_raise_random_exception(
        self, mock_random_function2: AsyncMock
    ) -> None:
        mock_random_function2.return_value = 4
        with self.assertRaises(RandomException):
            await random_function()
