import json
import sys
import requests
from datetime import datetime
from confluent_kafka import Consumer, Producer, TopicPartition, KafkaException

from admin.configuration import load_configuration, MANAGEMENT_TOPICS
from engine.matching_engine import MatchingEngine
from engine.transaction_status import TransactionStatus, TransactionReport
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

    consumer_group_id = "{}_consumer".format(paper_name)
    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9093",
            "group.id": consumer_group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "isolation.level": "read_committed",
        }
    )

    consumer.subscribe([paper_name])
    return consumer


def create_producer(paper_name):
    producer = Producer(
        {
            "bootstrap.servers": "localhost:9093",
            "transactional.id": "{}_producer".format(paper_name),
        }
    )
    producer.init_transactions()
    return producer


def producer_callback(err, msg_report):
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg_report.topic(), msg_report.partition()))


def generate_transaction_report(transaction_status: TransactionStatus, paper_name: str) -> TransactionReport:
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    return TransactionReport(
        id=transaction_status.id,
        count=transaction_status.count,
        transaction_value=transaction_status.transaction_value,
        name=paper_name,
        timestamp=timestamp_str,
    )


def main():
    paper_name = request_service()
    if paper_name == "UNKNOWN":
        print("Received service UNKNOWN!. Couldn't start service.")
        return

    config = load_configuration()
    consumer = create_consumer(paper_name, config)
    producer = create_producer(paper_name)
    matching_engine = MatchingEngine()

    print("Started {} engine".format(paper_name))
    sys.stdout.flush()
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        msg_commit_data = TopicPartition(topic=paper_name, offset=msg.offset() + 1, partition=msg.partition())
        msg_payload_str = msg.value().decode("utf-8")
        order = decode(json.loads(msg_payload_str))
        completed_stock_transactions = matching_engine.process(order)
        completed_stock_reports = [generate_transaction_report(st, paper_name) for st in completed_stock_transactions]

        try:
            producer.begin_transaction()
            for report in completed_stock_reports:
                producer.produce(
                    MANAGEMENT_TOPICS["transactions_completed_topic"],
                    report.json().encode("utf-8"),
                    callback=producer_callback,
                )
            producer.send_offsets_to_transaction(
                [msg_commit_data],
                consumer.consumer_group_metadata(),
            )
            producer.commit_transaction()
        except KafkaException as kafka_expection:
            # TODO: revert order book status here
            print("Transaction failed! Exception: {}".format(str(kafka_expection)))
            producer.abort_transaction()


if __name__ == "__main__":
    main()
