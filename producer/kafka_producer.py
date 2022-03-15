import json
from confluent_kafka import Producer
from fastapi import FastAPI

from admin.configuration import load_configuration
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder
from orders.cancel_order import CancelOrder


app = FastAPI()
producer = Producer({'bootstrap.servers': 'localhost:9093'})
config = load_configuration()


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def push_to_kafka(data: dict):
    producer.poll(0)
    producer.produce(data["name"], json.dumps(data).encode('utf-8'), callback=delivery_report)
    producer.flush()


def validate_request(data: dict):
    if data["name"] not in config["stock"]["papers"]:
        return False
    return True


def handle_order(order):
    data = json.loads(order.json())
    if validate_request(data):
        push_to_kafka(data)
        return {"transaction_status": "SUCCESS"}
    else:
        return {"transaction_status": "FAILED"}


@app.post("/market_order")
def handle_market_order(order: MarketOrder):
    return handle_order(order)


@app.post("/limit_order")
def handle_market_order(order: LimitOrder):
    return handle_order(order)


@app.post("/cancel_order")
def handle_cancel_order(order: CancelOrder):
    return handle_order(order)
