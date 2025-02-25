from beanie import PydanticObjectId
from fastapi import HTTPException
from app.db.models.wallet import Wallet
from app.utils.exception import RandomException


async def random_function2():
    return 10


async def random_function():
    if await random_function2() > 5:
        return True
    raise RandomException("Number is less than 5")


async def get_wallet(wallet_id: str) -> Wallet:
    wallet = await Wallet.find_one(
        Wallet.id == PydanticObjectId(wallet_id),
        {"is_deleted": False},
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist")
    return wallet
