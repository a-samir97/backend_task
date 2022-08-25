import environ

env = environ.Env()

environ.Env.read_env()

REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_PORT = env('REDIS_PORT', default=6379)
QUEUE_HOST = env('QUEUE_HOST', default='vernemq')
QUEUE_PORT = env('QUEUE_PORT', default=1883)
THNDR_TOPIC = env('THNDR_TOPIC', default='thndr-trading')
