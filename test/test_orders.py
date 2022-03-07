import pytest

from orders.limit_order import LimitOrder
from orders.cancel_order import CancelOrder
from orders.market_order import MarketOrder


def test_limit_order():
    order = LimitOrder(id="abcd", side="B", quantity=20, price=2)
    assert order.id == "abcd"
    assert order.quantity == 20


def test_cancel_order():
    order = CancelOrder(id="efgh")
    assert order.id == "efgh"


def test_market_order():
    order = MarketOrder(id="abcd", side="S", quantity=20)
    assert order.id == "abcd"
    assert order.side == "S"
    assert order.quantity == 20


def test_raise_if_wrong_id():
    with pytest.raises(ValueError):
        _ = CancelOrder(id="aaaad")


def test_raise_if_wrong_side():
    with pytest.raises(ValueError):
        _ = MarketOrder(id="aaaa", side="X", quantity=5)
