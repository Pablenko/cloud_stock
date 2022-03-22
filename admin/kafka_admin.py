import argparse
from confluent_kafka.admin import AdminClient, NewTopic
from admin.configuration import load_configuration, MANAGEMENT_TOPICS


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--reset", default=False, action="store_true",
                    help="Reset topic in case on invalid conf.")
    args = ap.parse_args()
    return args


def list_topics(admin):
    topics_meta = admin.list_topics()
    return [name for name in topics_meta.topics.keys() if not name.startswith("__")]


def validate_if_all_present(admin, stock_configuration):
    topics = list_topics(admin)
    papers = stock_configuration["stock"]["papers"]
    management_topics = list(MANAGEMENT_TOPICS.values())
    all_topics_required = papers + management_topics
    if len(topics) != len(all_topics_required):
        return False
    else:
        for topic in topics:
            if topic not in all_topics_required:
                return False
    return True


def _create_topics(admin, topic_list: list):
    fut_ret = admin.create_topics(topic_list)

    for topic, f in fut_ret.items():
        try:
            f.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


def create_stock_topics(admin, stock_configuration):
    topics = []
    for paper in stock_configuration["stock"]["papers"]:
        topics.append(NewTopic(paper, num_partitions=1, replication_factor=1))

    _create_topics(admin, topics)


def create_management_topics(admin):
    topics = [NewTopic(MANAGEMENT_TOPICS["transactions_completed_topic"], num_partitions=1, replication_factor=1)]
    _create_topics(admin, topics)


def delete_topics(admin):
    topics_to_delete = list_topics(admin)
    if len(topics_to_delete) == 0:
        return
    fut_ret = admin.delete_topics(topics_to_delete)

    for topic, f in fut_ret.items():
        try:
            f.result()
            print("Topic {} deleted".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))


def main():
    args = parse_args()
    admin = AdminClient({'bootstrap.servers': 'localhost:9093'})
    stock_configuration = load_configuration()
    valid = validate_if_all_present(admin, stock_configuration)
    if valid:
        print("Current topic configuration is valid!")
    else:
        print("Error! Current topic configuration is not valid!")
        if args.reset:
            delete_topics(admin)
            create_stock_topics(admin, stock_configuration)
            create_management_topics(admin)


if __name__ == "__main__":
    main()
