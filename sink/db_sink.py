import json
from confluent_kafka import Consumer
from admin.configuration import MANAGEMENT_TOPICS
from engine.transaction_status import TransactionReport
from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, inspect


def create_completed_consumer():
    consumer = Consumer(
        {
            "bootstrap.servers": "localhost:9093",
            "group.id": "completed_consumer",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "isolation.level": "read_committed",
        }
    )

    consumer.subscribe([MANAGEMENT_TOPICS["transactions_completed_topic"]])
    return consumer


def create_db_engine():
    db_string = "postgresql://admin:admin@localhost:5432/cloud_stock"
    db_engine = create_engine(db_string)
    return db_engine


def create_table(meta_data, db_engine):
    transactions_table = Table(
        "completed",
        meta_data,
        Column("id", String),
        Column("name", String),
        Column("timestamp", String),
        Column("count", Integer),
        Column("transaction_value", Integer),
    )
    if not inspect(db_engine).has_table("completed"):
        transactions_table.create()
    return transactions_table


def insert_data(db_engine, transaction_table, transaction_data):
    insert_statement = transaction_table.insert().values(
        id=transaction_data.id,
        name=transaction_data.name,
        timestamp=transaction_data.timestamp,
        count=transaction_data.count,
        transaction_value=transaction_data.transaction_value,
    )
    db_engine.execute(insert_statement)


def main():
    consumer = create_completed_consumer()
    db_engine = create_db_engine()
    db_meta_data = MetaData(db_engine)
    transactions_completed_table = create_table(db_meta_data, db_engine)

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        msg_payload_str = msg.value().decode("utf-8")
        msg_json = json.loads(msg_payload_str)
        transaction_data = TransactionReport(**msg_json)
        insert_data(db_engine, transactions_completed_table, transaction_data)
        print("Inserted data into db.")


if __name__ == "__main__":
    main()
