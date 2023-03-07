import redis


def create_redis() -> redis.ConnectionPool:
    pool = redis.ConnectionPool(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )
    return pool
