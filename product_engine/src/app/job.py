from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.generic_repo import CreateRepo, GenericRepository
from common.database import SessionLocal
from common import models
from common.schemas import MsgPaymentOverdue
from aiokafka import AIOKafkaProducer
import datetime
import traceback
import requests
import asyncio
import json
import os


async def send_to_origination(agreement, client):
    headers = {"Content-Type": "application/json"}
    data = agreement.to_dict()
    data["client_id"] = client.client_id
    data.pop("agreement_date")
    with open("logs.txt", "a") as file:
        file.write(f"send to orig {data}")
    r = requests.post("http://{}/application".format(os.getenv("ORIG_PATH")), headers=headers, params={"data":json.dumps(data)})
    with open("logs.txt", "a") as file:
        file.write(f"{r.status_code}\n")


async def pe_job():
    with open("logs.txt", "a") as file:
        file.write(f"in job")
    repo : GenericRepository = GenericRepository(SessionLocal(), models.Agreement)
    agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
    repo2 : GenericRepository = GenericRepository(SessionLocal(), models.Client)
    for agreement in agr:
        cli = repo2.get_by_condition(models.Client.client_id==agreement.client_id)[0]
        await send_to_origination(agreement, cli)

async def payment_job():
    repo = GenericRepository(SessionLocal(), models.SchedulePayment)
    repo_agr = GenericRepository(SessionLocal(), models.Agreement)
    current_date = datetime.datetime.now(datetime.timezone.utc)
    overdued_payments = repo.get_by_condition((models.SchedulePayment.payment_status=="FUTURE") & (models.SchedulePayment.expected_payment_date<current_date))
    repo.update_by_condition(models.SchedulePayment.expected_payment_date < current_date, "payment_status", "OVERDUE")
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    try:
        await producer.start()
        for payment in overdued_payments:
            msg = MsgPaymentOverdue(agreement_id = payment.agreement_id, 
                                    client_id = repo_agr.get_by_condition(models.Agreement.agreement_id==payment.agreement_id)[0].client_id,
                                    overdue_date = payment.expected_payment_date.isoformat(),
                                    payment = round(payment.principal_payment + payment.interest_payment, 2))
            try:
                await producer.send_and_wait(os.getenv("TOPIC_OVERDUED_PAYMENTS"), json.dumps(msg.dict()).encode("ascii"))
            except Exception:
                with open("logs.txt", "a") as file:
                    file.write(traceback.format_exc())
    finally:
        await producer.stop()


async def start_scheduler():
    with open("logs.txt", "a") as file:
        file.write(f"Started job\n")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(payment_job, 'interval', seconds=10)
    scheduler.add_job(pe_job, 'interval', seconds=10)
    scheduler.start()
    await asyncio.Event().wait()