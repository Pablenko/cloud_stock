import json
import sys
import requests
from confluent_kafka import Consumer

from admin.configuration import load_configuration
from engine.matching_engine import MatchingEngine
from service_discovery.service import SERVICE_DISCOVERY_PORT
from orders.codecs import decode


def request_service():
    request_address = "http://127.0.0.1:" + str(SERVICE_DISCOVERY_PORT) + "/request_service"
    response = requests.get(request_address)
    response_json = response.json()
    print(response_json)
    return response_json["SERVICE_NAME"]


def create_consumer(paper_name, stock_configuration):
    if paper_name not in stock_configuration["stock"]["papers"]:
        raise RuntimeError("Wrong stock paper name: {}".format(paper_name))

    consumer = Consumer({
        'bootstrap.servers': 'localhost:9093',
        'group.id': 'group_id',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    })

    consumer.subscribe([paper_name])
    return consumer


def main():
    paper_name = request_service()
    if paper_name == "UNKNOWN":
        print("Received service UNKNOWN!. Couldn't start service.")
        return

    print("Starting consumer for {}".format(paper_name))
    config = load_configuration()
    consumer = create_consumer(paper_name, config)
    matching_engine = MatchingEngine()

    print("Consumer {} started".format(paper_name))
    sys.stdout.flush()
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        msg_payload_str = msg.value().decode('utf-8')
        order = decode(json.loads(msg_payload_str))
        transaction_value = matching_engine.process(order)
        # It will change in next iteration. Not completed LimitOrders should not be committed, because
        # after engine crash OrderBook will be lost. Management of crash is under development.
        ret_val = consumer.commit(message=msg)
        print("Committed message, retval: {} transaction_val {}".format(ret_val, transaction_value))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
