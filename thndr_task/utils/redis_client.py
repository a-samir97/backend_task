import json
import redis
from redis.exceptions import ConnectionError
import logging

class RedisClient:
    """
        Redis client responsible for storing all information about stocks.
    """
    def __init__(self, host=None, port=None, db=0, password=None):
        """
        Create the redis client in one place so we change it once
        when we need to change any configurations
        """
        host = host
        port = port

        self.connection_err_msg = 'Error on connecting to redis on init, \
            exception: {}, restarting the service...'
        try:
            self.client = redis.Redis(host=host, port=port, db=db, password=password)
            self.client.ping()
        except (ConnectionRefusedError, ConnectionError) as e:
            logging.error(self.connection_err_msg.format(e))
            raise SystemExit
 
    def set_stock(self, name, key, value):
        self.__set_stock__(name, key, value)
    
    def get_stock(self, name, key):
        return self.__get_stock__(name, key)

    def __set_stock__(self, name, key, value):
        try:
            self.client.hset(name, key, json.dumps(value))
        except (ConnectionRefusedError, ConnectionError) as e:
            logging.error(self.connection_err_msg.format(e))
            raise SystemExit

    def __get_stock__(self, name, key):
        try:
            value = self.client.hget(name=name, key=key)
            return_value = None if value is None else json.loads(value)
        except (ConnectionRefusedError, ConnectionError) as e:
            logging.error(self.connection_err_msg.format(e))
            raise SystemExit
        return return_value
    