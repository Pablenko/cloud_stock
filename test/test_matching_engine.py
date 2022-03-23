from engine.matching_engine import MatchingEngine, LimitOrderWithContext
from engine.transaction_status import TransactionStatus
from orders.cancel_order import CancelOrder
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder


def test_matching_engine_cancel_order():
    engine = MatchingEngine()

    tr_report_1 = engine.process(LimitOrder(id="aaaa", name="intel", side="B", quantity=10, price=2))
    tr_report_2 = engine.process(CancelOrder(id="aaaa", name="intel"))

    assert engine.report() == {"B": [], "S": []}
    assert tr_report_1 == []
    assert tr_report_2 == [TransactionStatus(id="aaaa", count=0, transaction_value=0)]


def test_matching_engine_insert_limit_orders_which_wont_be_matched():
    engine = MatchingEngine()

    tr_report_1 = engine.process(LimitOrder(id="aaaa", name="intel", side="B", quantity=10, price=2))
    tr_report_2 = engine.process(LimitOrder(id="bbbb", name="intel", side="B", quantity=20, price=4))
    tr_report_3 = engine.process(LimitOrder(id="cccc", name="intel", side="S", quantity=30, price=6))

    assert engine.report() == {
        "B": [
            LimitOrderWithContext(
                id="bbbb", name="intel", side="B", quantity=20, price=4, total_transaction_value=0, total_quantity=20
            ),
            LimitOrderWithContext(
                id="aaaa", name="intel", side="B", quantity=10, price=2, total_transaction_value=0, total_quantity=10
            ),
        ],
        "S": [
            LimitOrderWithContext(
                id="cccc", name="intel", side="S", quantity=30, price=6, total_transaction_value=0, total_quantity=30
            )
        ],
    }
    assert tr_report_1 == []
    assert tr_report_2 == []
    assert tr_report_3 == []


def test_matching_engine_perform_sell_market_order():
    engine = MatchingEngine()

    tr_report_1 = engine.process(LimitOrder(id="aaaa", name="intel", side="B", quantity=20, price=5))
    tr_report_2 = engine.process(LimitOrder(id="bbbb", name="intel", side="B", quantity=10, price=6))
    tr_report_3 = engine.process(LimitOrder(id="cccc", name="intel", side="S", quantity=2, price=7))
    tr_report_4 = engine.process(MarketOrder(id="dddd", name="intel", side="S", quantity=25))

    assert engine.report() == {
        "B": [
            LimitOrderWithContext(
                id="aaaa", name="intel", side="B", quantity=5, price=5, total_transaction_value=75, total_quantity=20
            )
        ],
        "S": [
            LimitOrderWithContext(
                id="cccc", name="intel", side="S", quantity=2, price=7, total_transaction_value=0, total_quantity=2
            )
        ],
    }
    assert tr_report_1 == []
    assert tr_report_2 == []
    assert tr_report_3 == []
    assert tr_report_4 == [
        TransactionStatus(id="bbbb", count=10, transaction_value=60),
        TransactionStatus(id="dddd", count=25, transaction_value=60 + 75),
    ]


def test_matching_engine_buy_order_with_highest_price_has_priority():
    engine = MatchingEngine()

    _ = engine.process(LimitOrder(id="aaaa", name="intel", side="B", quantity=10, price=5))
    _ = engine.process(LimitOrder(id="bbbb", name="intel", side="B", quantity=10, price=6))
    _ = engine.process(LimitOrder(id="cccc", name="intel", side="B", quantity=10, price=7))
    tr_report_4 = engine.process(MarketOrder(id="dddd", name="intel", side="S", quantity=10))

    assert engine.report() == {
        "B": [
            LimitOrderWithContext(
                id="bbbb", name="intel", side="B", quantity=10, price=6, total_transaction_value=0, total_quantity=10
            ),
            LimitOrderWithContext(
                id="aaaa", name="intel", side="B", quantity=10, price=5, total_transaction_value=0, total_quantity=10
            ),
        ],
        "S": [],
    }
    assert tr_report_4 == [
        TransactionStatus(id="cccc", count=10, transaction_value=70),
        TransactionStatus(id="dddd", count=10, transaction_value=70),
    ]


def test_matching_engine_sell_order_with_lowest_price_has_priority():
    engine = MatchingEngine()

    _ = engine.process(LimitOrder(id="aaaa", name="intel", side="S", quantity=10, price=5))
    _ = engine.process(LimitOrder(id="bbbb", name="intel", side="S", quantity=10, price=6))
    _ = engine.process(LimitOrder(id="cccc", name="intel", side="S", quantity=10, price=7))
    tr_report_4 = engine.process(MarketOrder(id="dddd", name="intel", side="B", quantity=10))

    assert engine.report() == {
        "S": [
            LimitOrderWithContext(
                id="bbbb", name="intel", side="S", quantity=10, price=6, total_transaction_value=0, total_quantity=10
            ),
            LimitOrderWithContext(
                id="cccc", name="intel", side="S", quantity=10, price=7, total_transaction_value=0, total_quantity=10
            ),
        ],
        "B": [],
    }
    assert tr_report_4 == [
        TransactionStatus(id="aaaa", count=10, transaction_value=50),
        TransactionStatus(id="dddd", count=10, transaction_value=50),
    ]


def test_matching_engine_fully_processed_limit_order():
    engine = MatchingEngine()

    tr_report_1 = engine.process(LimitOrder(id="aaaa", name="intel", side="B", quantity=9, price=5))
    tr_report_2 = engine.process(LimitOrder(id="bbbb", name="intel", side="B", quantity=7, price=6))
    tr_report_3 = engine.process(LimitOrder(id="cccc", name="intel", side="S", quantity=10, price=4))

    assert engine.report() == {
        "S": [],
        "B": [
            LimitOrderWithContext(
                id="aaaa", name="intel", side="B", quantity=6, price=5, total_transaction_value=15, total_quantity=9
            )
        ],
    }
    assert tr_report_1 == []
    assert tr_report_2 == []
    assert tr_report_3 == [
        TransactionStatus(id="bbbb", count=7, transaction_value=42),
        TransactionStatus(id="cccc", count=10, transaction_value=42 + 15),
    ]


def test_matching_engine_partly_processed_limit_order():
    engine = MatchingEngine()

    tr_report_1 = engine.process(LimitOrder(id="aaaa", name="intel", side="S", quantity=9, price=15))
    tr_report_2 = engine.process(LimitOrder(id="bbbb", name="intel", side="S", quantity=7, price=14))
    tr_report_3 = engine.process(LimitOrder(id="cccc", name="intel", side="B", quantity=17, price=20))

    assert engine.report() == {
        "S": [],
        "B": [
            LimitOrderWithContext(
                id="cccc",
                name="intel",
                side="B",
                quantity=1,
                price=20,
                total_transaction_value=135 + 98,
                total_quantity=17,
            )
        ],
    }
    assert tr_report_1 == []
    assert tr_report_2 == []
    assert tr_report_3 == [
        TransactionStatus(id="bbbb", count=7, transaction_value=98),
        TransactionStatus(id="aaaa", count=9, transaction_value=135),
    ]
