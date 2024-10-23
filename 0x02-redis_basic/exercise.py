#!/usr/bin/env python3
""" handling module """
import uuid
from functools import wraps
from typing import Callable, Optional, Union

import redis


def call_history(method: Callable) -> Callable:
    """
    A decorator that logs the input and output of the decorated method.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Logs the arguments and the result of the method call.
        """
        meth_name = method.__qualname__
        self._redis.rpush(meth_name + ":inputs", str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(meth_name + ":outputs", output)
        return output

    return wrapper


def replay(method: Callable) -> None:
    """
    Retrieves and displays the history of method calls, showing both
    the inputs and outputs stored in Redis.
    """
    meth_name = method.__qualname__
    redis_db = method.__self__._redis
    inputs = redis_db.lrange(meth_name + ":inputs", 0, -1)
    outputs = redis_db.lrange(meth_name + ":outputs", 0, -1)

    print(f"{meth_name} was called {len(inputs)} times:")
    for input, output in zip(inputs, outputs):
        input = input.decode("utf-8")
        output = output.decode("utf-8")
        print(f"{meth_name}(*{input}) -> {output}")


def count_calls(method: Callable) -> Callable:
    """
    A decorator that tracks how many times a method is called.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Increments the call count every time the method is invoked.
        """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    """
    Cache class for managing data storage and retrieval using Redis.
    """

    def __init__(self) -> None:
        """
        Sets up a Redis instance and clears any pre-existing data.
        """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in Redis under a randomly generated UUID key and returns the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self,
        key: str,
        fn: Optional[Callable] = None,
    ) -> Union[str, bytes, int, float, None]:
        """
        Retrieves data from Redis using a key and optionally applies a function
        to transform the data before returning it. Returns None if the key doesn't exist.
        """
        value = self._redis.get(key)
        if value is not None and fn is not None:
            value = fn(value)
        return value

    def get_int(self, key: str) -> Union[int, None]:
        """
        Fetches the value from Redis and casts it to an integer.
        """
        return self.get(key, int)

    def get_str(self, key: str) -> Union[str, None]:
        """
        Fetches the value from Redis and converts it to a string.
        """
        return self.get(key, str)
