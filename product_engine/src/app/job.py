from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.generic_repo import CreateRepo, GenericRepository
from common.database import SessionLocal
from common import models
from util import update_status_new
from aiokafka import AIOKafkaProducer
import datetime
import requests
import asyncio
import os


# async def send_to_origination(agreement, client):
#     headers = {"Content-Type": "application/json"}
#     data = agreement.to_dict()
#     data.update(client.to_dict()) 
#     r = requests.post("http://{}/application".format(os.getenv("ORIG_PATH")), headers=headers, params={"data":data})
#     if r == 200:
#         update_status_new([agreement], CreateRepo(models.Agreement, SessionLocal()))


# async def pe_job():
#     repo : GenericRepository = GenericRepository(SessionLocal(), models.Agreement)
#     agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
#     repo2 : GenericRepository = GenericRepository(SessionLocal(), models.Client)
#     for agreement in agr:
#         cli = repo2.get_by_condition(models.Client.client_id==agreement.client_id)
#         await send_to_origination(agreement, cli)

async def payment_job():
    repo = GenericRepository(SessionLocal(), models.SchedulePayment)
    current_date = datetime.datetime.now()
    overdued_payments = repo.get_by_condition(models.SchedulePayment.expected_payment_date < current_date)
    repo.update_by_condition(models.SchedulePayment.expected_payment_date < current_date, "payment_status", "OVERDUE")
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    await producer.start()
    for payment in overdued_payments:
        msg = MsgPaymentOverdue()
        try:
            await producer.send_and_wait(os.getenv("TOPIC_OVERDUED_PAYMENTS"), json.dumps(msg.dict()).encode("ascii"))
        finally:
            await producer.stop()


async def start_scheduler():
    with open("logs.txt", "a") as file:
        file.write(f"Started job\n")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(payment_job, 'interval', seconds=10)
    scheduler.start()
    await asyncio.Event().wait()