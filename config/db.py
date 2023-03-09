import os
import redis
from dotenv import load_dotenv

load_dotenv()


def create_redis() -> redis.ConnectionPool:
    pool = redis.ConnectionPool(
        username=os.getenv("REDIS_USERNAME"),
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=os.getenv("REDIS_DB"),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True
    )
    return pool
