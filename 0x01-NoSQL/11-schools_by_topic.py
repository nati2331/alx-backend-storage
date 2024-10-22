#!/usr/bin/env python3
"""ask 11
"""


def schools_by_topic(mongo_collection, topic):
    """Returns list of school
    """
    topic_filter = {
        'topics': {
            '$elemMatch': {
                '$eq': topic,
            },
        },
    }
    return [doc for doc in mongo_collection.find(topic_filter)]
