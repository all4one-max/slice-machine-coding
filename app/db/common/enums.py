import enum


class random(str, enum.Enum):
    pass


class TransactionStatus(str, enum.Enum):
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class TransactionType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
