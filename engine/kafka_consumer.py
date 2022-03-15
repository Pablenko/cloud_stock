import argparse
from admin.configuration import load_configuration
from confluent_kafka import Consumer
from engine.matching_engine import MatchingEngine


def create_consumer(paper_name, stock_configuration):
    if paper_name not in stock_configuration["stock"]["papers"]:
        raise RuntimeError("Wrong stock paper name.")

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
    config = load_configuration()
    consumer = create_consumer(args.paper, config)
    matching_engine = MatchingEngine()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        print('Received message: {}'.format(msg.value().decode('utf-8')))

        #matching_engine.process(msg)

        ret_val = consumer.commit(message=msg)
        print("Committed message, retval: {}".format(ret_val))


if __name__ == "__main__":
    main()
