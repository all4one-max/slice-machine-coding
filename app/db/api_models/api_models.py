from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    user_name: str
    user_email: str
    phone_number: str


class AddMoneyToWalletRequest(BaseModel):
    amount: int
    wallet_id: str


class WithdrawMoneyFromWalletRequest(BaseModel):
    wallet_id: str
    amount: int


class TransferMoneyRequest(BaseModel):
    from_wallet_id: str
    to_wallet_id: str
    amount: int
