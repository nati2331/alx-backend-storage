#!/usr/bin/env python3
"""A module providing tools for caching HTTP requests and tracking access.
"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
"""Redis instance available at the module level.
"""


def data_cacher(method: Callable) -> Callable:
    """Decorator to cache the result of fetched data from a URL.
    """
    @wraps(method)
    def invoker(url) -> str:
        """Wrapper function responsible for handling caching logic.
        """
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """Fetches the content of a URL, stores the response in cache, 
    and tracks how often the URL is requested.
    """
    return requests.get(url).text
