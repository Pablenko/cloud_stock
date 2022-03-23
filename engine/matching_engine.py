from engine.order_book import OrderBook
from engine.transaction_status import TransactionStatus
from orders.base_order import BaseOrder
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder
from orders.cancel_order import CancelOrder


VERY_BIG_NUM = 1000000


class LimitOrderWithContext(LimitOrder):
    total_transaction_value: int
    total_quantity: int


class MatchingEngine:
    def __init__(self):
        self.book = OrderBook()
        self.completed_transactions = []

    def process(self, order: BaseOrder) -> list:
        if isinstance(order, LimitOrder):
            self._process_limit_order(order)
        elif isinstance(order, MarketOrder):
            self._process_market_order(order)
        else:
            self._process_cancel_order(order)

        completed_transactions = self.completed_transactions.copy()
        self.completed_transactions = []
        return completed_transactions

    def report(self) -> dict:
        return self.book.report()

    def _process_sell_offer(self, quantity, price):
        remaining_items = quantity
        transaction_value = 0

        while remaining_items > 0:
            buy_elem = self.book.peek_buy()
            if buy_elem is not None and price <= buy_elem.price:
                if buy_elem.quantity <= remaining_items:
                    remaining_items -= buy_elem.quantity
                    transaction_value += buy_elem.quantity * buy_elem.price
                    buy_elem.total_transaction_value += transaction_value
                    self.completed_transactions.append(
                        TransactionStatus(
                            id=buy_elem.id,
                            count=buy_elem.total_quantity,
                            transaction_value=buy_elem.quantity * buy_elem.price,
                        )
                    )
                    self.book.pop_buy()
                else:
                    buy_elem.quantity -= remaining_items
                    transaction_value += remaining_items * buy_elem.price
                    buy_elem.total_transaction_value += remaining_items * buy_elem.price
                    remaining_items = 0
                    break
            else:
                break

        return remaining_items, transaction_value

    def _process_buy_offer(self, quantity, price):
        remaining_items = quantity
        transaction_value = 0

        while remaining_items > 0:
            sell_item = self.book.peek_sell()
            if sell_item is not None and price >= sell_item.price:
                if sell_item.quantity <= remaining_items:
                    remaining_items -= sell_item.quantity
                    transaction_value += sell_item.quantity * sell_item.price
                    sell_item.total_transaction_value += transaction_value
                    self.completed_transactions.append(
                        TransactionStatus(
                            id=sell_item.id,
                            count=sell_item.total_quantity,
                            transaction_value=sell_item.quantity * sell_item.price,
                        )
                    )
                    self.book.pop_sell()
                else:
                    sell_item.quantity -= remaining_items
                    transaction_value += remaining_items * sell_item.price
                    sell_item.total_transaction_value += remaining_items * sell_item.price
                    remaining_items = 0
                    break
            else:
                break

        return remaining_items, transaction_value

    def _process_market_order(self, order: MarketOrder):
        if order.side == "S":
            items_left, transaction_value = self._process_sell_offer(order.quantity, 0)
        else:
            items_left, transaction_value = self._process_buy_offer(order.quantity, VERY_BIG_NUM)

        self.completed_transactions.append(
            TransactionStatus(
                id=order.id,
                count=order.quantity - items_left,
                transaction_value=transaction_value,
            )
        )

    def _process_limit_order(self, order: LimitOrder):
        if order.side == "S":
            items_left, transaction_value = self._process_sell_offer(order.quantity, order.price)
        else:
            items_left, transaction_value = self._process_buy_offer(order.quantity, order.price)

        if items_left > 0:
            self.book.insert(
                LimitOrderWithContext(
                    id=order.id,
                    name=order.name,
                    price=order.price,
                    quantity=items_left,
                    side=order.side,
                    total_transaction_value=transaction_value,
                    total_quantity=order.quantity,
                )
            )
        else:
            self.completed_transactions.append(
                TransactionStatus(
                    id=order.id,
                    count=order.quantity,
                    transaction_value=transaction_value,
                )
            )

    def _process_cancel_order(self, order: CancelOrder):
        self.book.remove(order.id)
        self.completed_transactions.append(TransactionStatus(id=order.id, count=0, transaction_value=0))
