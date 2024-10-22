#!/usr/bin/env python3
"""
Changes topics
"""


def update_topics(mongo_collection, name, topics):
    """
    changes all topics
    """
    mongo_collection.update_many({"name": name}, {"$set": {"topics": topics}})
