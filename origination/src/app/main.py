from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import CreateRepo, GenericRepository
from util import create_agreement, check_and_delete_agr
from common import models
from common.database import SessionLocal, engine
from aiokafka import AIOKafkaConsumer
import asyncio
import os
import uvicorn
from job import scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

async def consume():
    consumer = AIOKafkaConsumer(
        os.getenv("TOPIC_AGREEMENTS"),
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    await consumer.start()
    try:
        async for message in consumer:
            with open("logs.txt", "w") as file:
                file.write(f"Received: {message.value.decode()}, topic: {message.topic}, offset: {message.offset}")
            print(f"Received: {message.value.decode()}, topic: {message.topic}, offset: {message.offset}")
    finally:
        await consumer.stop()

@app.on_event("startup")
async def startup_event():
    task = asyncio.create_task(consume())
    app.state.consumer_task = task

@app.on_event("shutdown")
async def shutdown_event():
    app.state.consumer_task.cancel()
    await app.state.consumer_task

@app.post("/application", summary="Create an application, agreement + client info should be provided in json")
def post_app(data, repo: GenericRepository = Depends(CreateRepo(models.Client, SessionLocal())), repo2: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal()))):
    application = create_agreement(repo, repo2, data)
    headers = {"Content-Type": "application/json"}
    if (application == -1):
        raise HTTPException(status_code=409, detail="Application already exists")
    return application


@app.post("/application/{application_id}/close", summary="Close application. application_id = agreement_id")
def delete_app(application_id, repo: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal()))):
    status = check_and_delete_agr(repo, application_id)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")


if __name__ == '__main__':
    scheduler.start()
    uvicorn.run(app, port=os.getenv("PORT"), host=os.getenv("HOST"))