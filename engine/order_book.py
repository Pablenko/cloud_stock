from heapq import heappush, heappop, heapify


class MaxHeapObj(object):
    def __init__(self, order): self.order = order
    def __lt__(self, other): return self.order.price > other.order.price
    def __eq__(self, other): return self.order.price == other.order.price


class MinHeapObj(object):
    def __init__(self, order): self.order = order
    def __lt__(self, other): return self.order.price < other.order.price
    def __eq__(self, other): return self.order.price == other.order.price


class OrderBook:
    def __init__(self):
        self.buy_book = []
        self.sell_book = []

    def insert(self, order):
        if order.side == "S":
            heappush(self.sell_book, MinHeapObj(order))
        else:
            heappush(self.buy_book, MaxHeapObj(order))

    def remove(self, order_id: str):
        def remove_helper(book):
            for idx, buy_elem in enumerate(book):
                if buy_elem.order.id == order_id:
                    del book[idx]
                    heapify(book)
                    break

        remove_helper(self.buy_book)
        remove_helper(self.sell_book)

    def peek_sell(self):
        if len(self.sell_book) > 0:
            return self.sell_book[0].order
        else:
            return None

    def peek_buy(self):
        if len(self.buy_book) > 0:
            return self.buy_book[0].order
        else:
            return None

    def pop_buy(self):
        del self.buy_book[0]
        heapify(self.buy_book)

    def pop_sell(self):
        del self.sell_book[0]
        heapify(self.sell_book)

    def report(self) -> dict:
        buy_book_copy = self.buy_book.copy()
        sell_book_copy = self.sell_book.copy()
        buy_book_report = [heappop(buy_book_copy).order for _ in range(len(buy_book_copy))]
        sell_book_report = [heappop(sell_book_copy).order for _ in range(len(sell_book_copy))]

        return {"B": buy_book_report, "S": sell_book_report}
