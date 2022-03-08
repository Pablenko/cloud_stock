from fastapi import FastAPI

from engine.matching_engine import MatchingEngine
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder
from orders.cancel_order import CancelOrder


app = FastAPI()
engine = MatchingEngine()


@app.post("/market_order")
def handle_market_order(order: MarketOrder):
    transaction_value = engine.process(order)
    return {"transaction_value": transaction_value}


@app.post("/limit_order")
def handle_market_order(order: LimitOrder):
    transaction_value = engine.process(order)
    return {"transaction_value": transaction_value}


@app.post("/cancel_order")
def handle_cancel_order(order: CancelOrder):
    transaction_value = engine.process(order)
    return {"transaction_value": transaction_value}


@app.get("/book")
def handle_book_request():
    book = engine.report()
    return book
