#!/usr/bin/env python3
'''A module for caching web requests and monitoring request counts.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''Redis instance used at the module scope.
'''


def data_cacher(method: Callable) -> Callable:
    '''Decorator to store the results of data retrieval in the cache.
    '''
    @wraps(method)
    def invoker(url) -> str:
        '''A wrapper function that handles the caching mechanism.
        '''
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
    '''Fetches the content of the URL, stores it in the cache, 
    and keeps track of how many times the URL is accessed.
    '''
    return requests.get(url).text
