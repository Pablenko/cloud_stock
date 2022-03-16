import argparse
import json
import sys
from confluent_kafka import Consumer

from admin.configuration import load_configuration
from engine.matching_engine import MatchingEngine
from orders.codecs import decode


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


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--paper", required=True, type=str, help="Name of paper for which subscribe to.")
    args = ap.parse_args()
    return args


def main():
    args = parse_args()
    print("Starting consumer for {}".format(args.paper))
    config = load_configuration()
    consumer = create_consumer(args.paper, config)
    matching_engine = MatchingEngine()

    print("Consumer {} started".format(args.paper))
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        msg_payload_str = msg.value().decode('utf-8')
        print('Received message: {}'.format(msg_payload_str))
        order = decode(json.loads(msg_payload_str))
        transaction_value = matching_engine.process(order)
        ret_val = consumer.commit(message=msg)
        print("Committed message, retval: {} transaction_val {}".format(ret_val, transaction_value))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
