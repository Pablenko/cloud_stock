import argparse
from confluent_kafka.admin import AdminClient, NewTopic
from admin.configuration import load_configuration


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
    if len(topics) != len(papers):
        return False
    else:
        for topic in topics:
            if topic not in papers:
                return False
    return True


def create_topics(admin, stock_configuration):
    topics = []
    for paper in stock_configuration["stock"]["papers"]:
        topics.append(NewTopic(paper, num_partitions=1, replication_factor=1))

    fut_ret = admin.create_topics(topics)

    for topic, f in fut_ret.items():
        try:
            f.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


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
            create_topics(admin, stock_configuration)


if __name__ == "__main__":
    main()
