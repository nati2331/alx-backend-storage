#!/usr/bin/env python3
"""
Task 14
"""


def top_students(mongo_collection):
    """
    returns inorder of score
    """
    return mongo_collection.aggregate([
        {"$project": {
            "name": "$name",
            "averageScore": {"$avg": "$topics.score"}
        }},
        {"$sort": {"averageScore": -1}}
    ])
