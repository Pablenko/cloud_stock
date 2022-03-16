from orders.limit_order import LimitOrder
from orders.cancel_order import CancelOrder
from orders.market_order import MarketOrder
from orders.base_order import BaseOrder


def encode(payload: dict, msg_type: str) -> dict:
    return {"type": msg_type, "payload": payload}


def decode(msg: dict) -> BaseOrder:
    msg_type = msg["type"]

    if msg_type == "market_order":
        return MarketOrder(**msg["payload"])
    elif msg_type == "limit_order":
        return LimitOrder(**msg["payload"])
    else:
        return CancelOrder(**msg["payload"])
