from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from common.generic_repo import CreateRepo, GenericRepository
from common import models
from common.schemas import MsgToScoring
from common.database import SessionLocal
from aiokafka import AIOKafkaProducer
import asyncio
import json
import os
import traceback
import requests

async def send_to_scoring(agreements):
    producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_INSTANCE"))
    await producer.start()
    for agr in agreements:
        msg = MsgToScoring(
        name="kafka produce from origination",
        agreement_id=agr.agreement_id,
        product_id=agr.product_id,
        client_id=agr.client_id,
        )
        with open("logs.txt", "a") as file:
            file.write(f"agr{agr.agreement_id}, topic{os.getenv('TOPIC_SCORING_REQUEST')}\n")
        await producer.send_and_wait(os.getenv("TOPIC_SCORING_REQUEST"), json.dumps(msg.dict()).encode("ascii"))
        with open("logs.txt", "a") as file:
            file.write(f"sent\n")
    await producer.stop()

async def orig_job():
    repo = GenericRepository(SessionLocal(), models.Application)
    try:
        agr = repo.get_by_condition(models.Application.agreement_status == "NEW")
        repo.update_by_condition(models.Application.agreement_status == "NEW", "agreement_status", "SCORING")
        await send_to_scoring(agr)
    except Exception:
        with open("logs.txt", "a") as file:
            file.write(traceback.format_exc())

async def start_scheduler():
    with open("logs.txt", "a") as file:
        file.write(f"Started job\n")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(orig_job, 'interval', seconds=10)
    scheduler.start()
    await asyncio.Event().wait()
