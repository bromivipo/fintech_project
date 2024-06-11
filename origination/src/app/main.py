from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import CreateRepo, GenericRepository
from util import create_application, check_and_delete_application, set_application_status
from common import models
from common.database import SessionLocal, engine
from aiokafka import AIOKafkaConsumer
import asyncio
import json
import traceback
import os
import uvicorn
from job import start_scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

async def consume(topic, func, repo=GenericRepository(SessionLocal(), models.Application)):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    await consumer.start()
    try:
        async for message in consumer:
            with open("logs.txt", "a") as file:
                file.write(f"Received: {message.value.decode()}, topic: {message.topic}, offset: {message.offset}\n")
            func(repo, message.value.decode())
    except Exception:
        with open("logs.txt", "a") as file:
            file.write(traceback.format_exc())
    finally:
        with open("logs.txt", "a") as file:
            file.write(f"Stopped")
        await consumer.stop()

@app.post("/application", summary="Create an application, agreement + client info should be provided in json")
def post_app(data, repo: GenericRepository = Depends(CreateRepo(models.Application, SessionLocal()))):
    application = create_application(repo, data)
    if (application == -1):
        raise HTTPException(status_code=409, detail="Application already exists")
    return application


@app.post("/application/{application_id}/close", summary="Close application. application_id = agreement_id")
def delete_app(application_id, repo: GenericRepository = Depends(CreateRepo(models.Application, SessionLocal()))):
    status = check_and_delete_application(repo, application_id)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")


if __name__=='__main__':
    with open("logs.txt", "a") as file:
        file.write(f"Started\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(start_scheduler())
    loop.create_task(consume(os.getenv("TOPIC_AGREEMENTS"),
                                create_application))
    loop.create_task(consume(os.getenv("TOPIC_SCORING_RESPONSE"),
                             set_application_status))
    
    config = uvicorn.Config(
        app=app,
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        loop=loop
    )
    server = uvicorn.Server(config)
    server_task = asyncio.ensure_future(server.serve())
    loop.run_until_complete(server_task)