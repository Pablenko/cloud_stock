import json
from confluent_kafka import Producer, KafkaException
from fastapi import FastAPI

from admin.configuration import load_configuration
from orders.codecs import encode
from orders.base_order import BaseOrder
from orders.limit_order import LimitOrder
from orders.market_order import MarketOrder
from orders.cancel_order import CancelOrder


app = FastAPI()
producer = Producer({'bootstrap.servers': 'localhost:9093',
                     'transactional.id': 'producer_1_id'})
config = load_configuration()
producer.init_transactions()


def push_to_kafka(topic_name: str, msg: dict) -> bool:
    delivery_status = False

    def delivery_report(err, msg_report):
        nonlocal delivery_status
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            delivery_status = True
            print('Message delivered to {} [{}]'.format(msg_report.topic(), msg_report.partition()))

    try:
        producer.begin_transaction()
        producer.produce(topic_name, json.dumps(msg).encode('utf-8'), callback=delivery_report)
        producer.commit_transaction()
    except KafkaException as kafka_expection:
        print("Transaction failed! Exception: {}".format(str(kafka_expection)))
        producer.abort_transaction()
    else:
        delivery_status = True

    return delivery_status


def validate_request(topic_name: str):
    if topic_name not in config["stock"]["papers"]:
        return False
    return True


def handle_order(order: BaseOrder, order_type: str):
    data = json.loads(order.json())
    topic_name = data["name"]
    if validate_request(topic_name):
        msg = encode(data, order_type)
        delivery_status = push_to_kafka(topic_name, msg)
        if delivery_status:
            return {"transaction_status": "SUCCESS"}

    return {"transaction_status": "FAILED"}


@app.post("/market_order")
def handle_market_order(order: MarketOrder):
    return handle_order(order, "market_order")


@app.post("/limit_order")
def handle_limit_order(order: LimitOrder):
    return handle_order(order, "limit_order")


@app.post("/cancel_order")
def handle_cancel_order(order: CancelOrder):
    return handle_order(order, "cancel_order")
