from pydantic import validator
from orders.base_order import BaseOrder, side_validator


class MarketOrder(BaseOrder):
    side: str
    quantity: int

    @validator("side")
    def validate_side(cls, matched_side):
        return side_validator(matched_side)
