import uvicorn
import os

from fastapi import FastAPI, Depends, status, Response
from cryptography.fernet import Fernet
from redis import Redis
from shortuuid import uuid

from config import db
from models import message

from typing import Any


# info_logger = logging.getLogger("uvicorn.info")
app = FastAPI()


# async def lifespan(app: FastAPI):
#     yield


def conn_redis():
    print("INFO:     Connecting to Redis database")

    pool = db.create_redis()

    return Redis(connection_pool=pool)


@app.get("/api/v1")
async def index():
    return {"home": "go to routes create or retrieve, enjoy <3"}


@app.post("/api/v1/create", status_code=status.HTTP_201_CREATED)
async def create(
        res: Response,
        message: message.Message,
        client: Any = Depends(conn_redis)):
    id: str = uuid()
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(bytes(message.content, "utf-8"))

    result = client.hset(
        f"messages:{id}",
        mapping={"key": key, "content": token}
    )

    if result == 0:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error at save message"}

    return {"id": id}


@app.post("/api/v1/retrieve/{message_id}", status_code=status.HTTP_200_OK)
async def decrypt(
        res: Response,
        message_id: str,
        client: Any = Depends(conn_redis)):
    pipeline = client.pipeline()

    pipeline.hgetall(f"messages:{message_id}")
    pipeline.delete(f"messages:{message_id}")

    result = pipeline.execute()

    if not any(result[0].values()):
        res.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "this messasge not exist or already was readed"}

    f = Fernet(result[0]["key"])

    return {"message": f.decrypt(result[0]["content"])}


if __name__ == "__main__":
    port = os.getenv("PORT")

    if port is None:
        port = "8080"

    uvicorn.run(app, host="0.0.0.0", port=int(port))
