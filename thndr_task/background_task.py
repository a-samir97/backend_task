import json
import paho.mqtt.client as mqtt 

from utils import RedisClient
from thndr_task import env

# Redis client to store stocks info in redis database
redis_client = RedisClient(host=env.REDIS_HOST, port=env.REDIS_PORT, db=0)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(env.THNDR_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    stock = json.loads(msg.payload)

    redis_client.set_stock(
        name='stocks',
        key=stock['name'],
        value={
            'stock_id': stock['stock_id'],
            'price': stock['price'],
            'availability': stock['availability'],
            'timestamp': stock['timestamp']
        }
    )

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(env.QUEUE_HOST, env.QUEUE_PORT, 60)
client.loop_forever()
