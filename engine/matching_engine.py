from engine.order_book import OrderBook
from orders.base_order import BaseOrder
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder
from orders.cancel_order import CancelOrder


VERY_BIG_NUM = 1000000


class MatchingEngine:
    def __init__(self):
        self.book = OrderBook()

    def process(self, order: BaseOrder):
        if isinstance(order, LimitOrder):
            return self._process_limit_order(order)
        elif isinstance(order, MarketOrder):
            return self._process_market_order(order)
        else:
            return self._process_cancel_order(order)

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
                    self.book.pop_buy()
                else:
                    buy_elem.quantity -= remaining_items
                    transaction_value += remaining_items * buy_elem.price
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
                    self.book.pop_sell()
                else:
                    sell_item.quantity -= remaining_items
                    transaction_value += remaining_items * sell_item.price
                    remaining_items = 0
                    break
            else:
                break

        return remaining_items, transaction_value

    def _process_market_order(self, order: MarketOrder):
        if order.side == "S":
            _, transaction_value = self._process_sell_offer(order.quantity, 0)
        else:
            _, transaction_value = self._process_buy_offer(order.quantity, VERY_BIG_NUM)

        return transaction_value

    def _process_limit_order(self, order: LimitOrder):
        if order.side == "S":
            items_left, transaction_value = self._process_sell_offer(order.quantity, order.price)
        else:
            items_left, transaction_value = self._process_buy_offer(order.quantity, order.price)

        if items_left > 0:
            self.book.insert(LimitOrder(id=order.id, name=order.name, price=order.price, quantity=items_left,
                                        side=order.side))

        return transaction_value

    def _process_cancel_order(self, order: CancelOrder):
        self.book.remove(order.id)
        return 0
