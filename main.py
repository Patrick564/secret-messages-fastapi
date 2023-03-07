from fastapi import FastAPI, Depends
from cryptography.fernet import Fernet
from pydantic import BaseModel
from redis import Redis, ConnectionPool
from shortuuid import uuid

from typing import Any


class Message(BaseModel):
    content: str


app = FastAPI()


def conn_redis():
    pool = ConnectionPool(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )
    return Redis(connection_pool=pool)


@app.post("/api/v1/create")
def create(message: Message, client: Redis[str] = Depends(conn_redis)):
    id: str = uuid()
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(bytes(message.content, "utf-8"))

    client.hset(f"messages:{id}", mapping={"key": key, "message": token})

    return {"id": id}


@app.post("/api/v1/retrieve/{message_id}")
def decrypt(message_id: str, client: Any = Depends(conn_redis)):
    message = client.hgetall(f"messages:{message_id}")
    client.delete(f"messages:{message_id}")
    f = Fernet(message["key"])

    return {"message": f.decrypt(message["message"])}
