from engine.matching_engine import MatchingEngine
from orders.cancel_order import CancelOrder
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder


def test_matching_engine_cancel_order():
    engine = MatchingEngine()

    engine.process(LimitOrder(id="aaaa", side="B", quantity=10, price=2))
    engine.process(CancelOrder(id="aaaa"))

    assert engine.report() == {"B": [], "S": []}


def test_matching_engine_insert_limit_orders():
    engine = MatchingEngine()

    engine.process(LimitOrder(id="aaaa", side="B", quantity=10, price=2))
    engine.process(LimitOrder(id="bbbb", side="B", quantity=20, price=4))
    engine.process(LimitOrder(id="cccc", side="S", quantity=30, price=6))

    assert engine.report() == {"B": [LimitOrder(id="bbbb", side="B", quantity=20, price=4),
                                     LimitOrder(id="aaaa", side="B", quantity=10, price=2)],
                               "S": [LimitOrder(id="cccc", side="S", quantity=30, price=6)]}


def test_matching_engine_perform_sell_market_order():
    engine = MatchingEngine()

    engine.process(LimitOrder(id="aaaa", side="B", quantity=20, price=5))
    engine.process(LimitOrder(id="bbbb", side="B", quantity=10, price=6))
    engine.process(LimitOrder(id="cccc", side="S", quantity=2, price=7))
    engine.process(MarketOrder(id="dddd", side="S", quantity=25))

    assert engine.report() == {"B": [LimitOrder(id="aaaa", side="B", quantity=5, price=5)],
                               "S": [LimitOrder(id="cccc", side="S", quantity=2, price=7)]}


def test_matching_engine_buy_order_with_highest_price_has_priority():
    engine = MatchingEngine()

    engine.process(LimitOrder(id="aaaa", side="B", quantity=10, price=5))
    engine.process(LimitOrder(id="bbbb", side="B", quantity=10, price=6))
    engine.process(LimitOrder(id="cccc", side="B", quantity=10, price=7))
    engine.process(MarketOrder(id="dddd", side="S", quantity=10))

    assert engine.report() == {"B": [LimitOrder(id="bbbb", side="B", quantity=10, price=6),
                                     LimitOrder(id="aaaa", side="B", quantity=10, price=5)],
                               "S": []}


def test_matching_engine_sell_order_with_lowest_price_has_priority():
    engine = MatchingEngine()

    engine.process(LimitOrder(id="aaaa", side="S", quantity=10, price=5))
    engine.process(LimitOrder(id="bbbb", side="S", quantity=10, price=6))
    engine.process(LimitOrder(id="cccc", side="S", quantity=10, price=7))
    engine.process(MarketOrder(id="dddd", side="B", quantity=10))

    assert engine.report() == {"S": [LimitOrder(id="bbbb", side="S", quantity=10, price=6),
                                     LimitOrder(id="cccc", side="S", quantity=10, price=7)],
                               "B": []}


def test_matching_engine_fully_processed_limit_order():
    engine = MatchingEngine()

    transaction_1 = engine.process(LimitOrder(id="aaaa", side="B", quantity=9, price=5))
    transaction_2 = engine.process(LimitOrder(id="bbbb", side="B", quantity=7, price=6))
    transaction_3 = engine.process(LimitOrder(id="cccc", side="S", quantity=10, price=4))

    assert transaction_1 == 0
    assert transaction_2 == 0
    assert transaction_3 == 7*6 + 3*5
    assert engine.report() == {"S": [],
                               "B": [LimitOrder(id="aaaa", side="B", quantity=6, price=5)]}


def test_matching_engine_partly_processed_limit_order():
    engine = MatchingEngine()

    transaction_1 = engine.process(LimitOrder(id="aaaa", side="S", quantity=9, price=15))
    transaction_2 = engine.process(LimitOrder(id="bbbb", side="S", quantity=7, price=14))
    transaction_3 = engine.process(LimitOrder(id="cccc", side="B", quantity=17, price=20))

    assert transaction_1 == 0
    assert transaction_2 == 0
    assert transaction_3 == 9*15 + 7*14
    assert engine.report() == {"S": [],
                               "B": [LimitOrder(id="cccc", side="B", quantity=1, price=20)]}
