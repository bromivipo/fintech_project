from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import GenericRepository
from util import create_application, check_and_close_application, set_application_status
from common.models.base import Base
from common.models.application import Application
from common.database import engine, get_db
from common.kafka_common import consume
import asyncio
import os
import uvicorn
from job import start_scheduler

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/application", summary="Create an application, agreement + client info should be provided in json")
def post_app(data):
    application = create_application(data)
    if (application == -1):
        raise HTTPException(status_code=409, detail="Application already exists")
    return application


@app.post("/application/{application_id}/close", summary="Close application. application_id = agreement_id")
def delete_app(application_id, db = Depends(get_db)):
    repo = GenericRepository(db, Application)
    status = check_and_close_application(repo, application_id)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")


if __name__=='__main__':
    with open("logs.txt", "a") as file:
        file.write(f"Started\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(start_scheduler())
    loop.create_task(consume(os.getenv("TOPIC_AGREEMENTS"), "orig1",
                            create_application))
    loop.create_task(consume(os.getenv("TOPIC_SCORING_RESPONSE"), "orig2",
                             set_application_status))
    
    config = uvicorn.Config(
        app=app,
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        loop=loop
    )
    server = uvicorn.Server(config)
    server_task = asyncio.ensure_future(server.serve())
    loop.run_until_complete(server_task)

    loop.close()