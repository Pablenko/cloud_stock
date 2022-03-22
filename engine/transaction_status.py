from pydantic import BaseModel


class TransactionStatus(BaseModel):
    id: str
    count: int
    transaction_value: int


class TransactionReport(TransactionStatus):
    name: str
    timestamp: str
