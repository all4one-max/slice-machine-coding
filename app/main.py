from contextlib import asynccontextmanager
import logging
from beanie import PydanticObjectId
from fastapi import FastAPI, HTTPException

from app.db.api_models.api_models import (
    AddMoneyToWalletRequest,
    CreateUserRequest,
    TransferMoneyRequest,
    WithdrawMoneyFromWalletRequest,
)
from app.db.common.const import MAX_WALLET_BALANCE
from app.db.common.db import setup_db
from app.db.common.enums import TransactionStatus
from app.db.models.transaction import Transaction
from app.db.models.user import User
from app.db.models.wallet import Wallet
from app.utils.exception import UserDoesNotExistException
from app.utils.setup_logger import setup_logger
from app.utils.util import get_wallet

"""
Wallet System
Objective:
Design and implement a backend service that allows users to manage their wallets, transfer funds, and track transactions.
 
Functional Requirements
Wallet Management
1. Create a wallet for a user. -> create_wallet(user_id)
2. Retrieve wallet balance. -> get_wallet_balance(wallet_id)
3. List all transactions for a wallet.
Funds Management
4. Add money to a wallet (top-up from an external source).
5. Withdraw money from a wallet to an external source.
Money Transfer
6. Transfer funds between wallets, ensuring sufficient balance.
Transaction History & Reporting
7. Fetch transaction history with filters (date range, type).
 
Non-Functional Requirements
· Expose a RESTful API with appropriate HTTP methods.
· Ensure secure and consistent money transfers.
· Handle concurrent transactions efficiently.
· Write basic unit tests for key functionalities.
 
Constraints:
· A user’s wallet has a maximum balance limit.
· All transactions must be atomic to avoid inconsistencies.
 
Expected Deliverables:
· A structured backend service for wallet and transaction management.
· API endpoints for wallet operations.
· Readable, maintainable code following best practices.
· Unit tests covering key functionalities.

1. DB Schema Design:
User, 
Wallet -> User'
Transaction -> linked to wallet

User -> uid, name, user metadata
wallet -> wallet_id, user, cur_balance Link[User]
transaction -> wallet, from_user, to_user, amount

WALLET_MAX_BALANCE
create_wallet(user_id) POST
get_wallet_balance(wallet_id) GET
list_transaction(wallet_id) GET
add_money(wallet_id, amount) PUT
withdraw_money(wallet_id, amount) PUT
transfer_money(from_wallet_id, to_wallet_id, amount) -> potential raise exceptions PUT
fetch_transaction_history(user_id, query) GET

"""

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup mongo database
    await setup_db()
    # setup the logger
    setup_logger()

    yield


app = FastAPI(
    title="Slice Machine Coding Round",
    description="application made during slice machine coding round",
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/create_user")
async def create_user(create_user_request: CreateUserRequest):
    user = User(
        name=create_user_request.user_name,
        email_id=create_user_request.user_email,
        phone_numer=create_user_request.phone_number,
        wallet_ids=[],
    )
    await user.save()
    return user


@app.get("/get_all_users")
async def get_all_users():
    users = await User.find({"is_deleted": False}).to_list()
    return users


@app.post("/create_wallet/{user_id}")
async def create_wallet(user_id: str):
    user = await User.find_one(
        User.id == PydanticObjectId(user_id), {"is_deleted": False}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    wallet = Wallet(user_id=user_id, max_balance=MAX_WALLET_BALANCE, cur_balance=0)
    await wallet.save()
    user.wallet_ids.append(str(wallet.id))
    await user.save()

    return str(wallet.id)


@app.get("/get_wallet_balance/{wallet_id}")
async def get_wallet_balance(wallet_id: str):
    wallet = await Wallet.find_one(
        Wallet.id == PydanticObjectId(wallet_id), {"is_deleted": False}
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist")
    return wallet.cur_balance


@app.put("/add_money_to_wallet")
async def add_money_to_wallet(add_money_to_wallet: AddMoneyToWalletRequest) -> bool:
    wallet = await Wallet.find_one(
        Wallet.id == PydanticObjectId(add_money_to_wallet.wallet_id),
        {"is_deleted": False},
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet does not exist")

    if add_money_to_wallet.amount < 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if (wallet.cur_balance + add_money_to_wallet.amount) > wallet.max_balance:
        raise HTTPException(status_code=400, detail="Exceeds wallet balance limit")

    wallet.cur_balance += add_money_to_wallet.amount
    await wallet.save()
    return True


@app.put("/withdraw_money_from_wallet")
async def withdraw_money_from_wallet(
    withdraw_money_from_wallet: WithdrawMoneyFromWalletRequest,
):
    wallet: Wallet = await get_wallet(withdraw_money_from_wallet.wallet_id)

    if withdraw_money_from_wallet.amount < 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if wallet.cur_balance < withdraw_money_from_wallet.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    wallet.cur_balance -= withdraw_money_from_wallet.amount
    await wallet.save()
    return True


@app.put("/transfer_money")
async def transfer_money(transfer_money_request: TransferMoneyRequest):
    try:
        if transfer_money_request.amount < 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        from_wallet: Wallet = await get_wallet(transfer_money_request.from_wallet_id)

        to_wallet: Wallet = await get_wallet(transfer_money_request.to_wallet_id)

        if from_wallet.cur_balance < transfer_money_request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        if (
            to_wallet.cur_balance + transfer_money_request.amount
        ) > to_wallet.max_balance:
            raise HTTPException(status_code=400, detail="Exceeds wallet balance limit")

        from_wallet.cur_balance -= transfer_money_request.amount
        to_wallet.cur_balance += transfer_money_request.amount
        await from_wallet.save()
        await to_wallet.save()

        transaction = Transaction(
            from_wallet_id=str(from_wallet.id),
            to_wallet_id=str(to_wallet.id),
            amount=transfer_money_request.amount,
            transaction_status=TransactionStatus.COMPLETED,
        )
        await transaction.save()

        return True
    except Exception:
        transaction = Transaction(
            from_wallet_id=str(transfer_money_request.from_wallet_id),
            to_wallet_id=str(transfer_money_request.to_wallet_id),
            amount=transfer_money_request.amount,
            transaction_status=TransactionStatus.FAILED,
        )
        await transaction.save()
