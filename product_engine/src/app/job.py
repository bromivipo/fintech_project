from apscheduler.schedulers.background import BackgroundScheduler
from common.generic_repo import CreateRepo, GenericRepository
from common.database import SessionLocal
from common import models
from util import update_status_new
import requests
import os


def send_to_origination(agreement, client):
    headers = {"Content-Type": "application/json"}
    r = requests.post("http://{}/application".format(os.getenv("ORIG_PATH")), headers=headers, params={"data": dict(agreement).update(dict(client))})
    if r == 200:
        update_status_new([agreement], CreateRepo(models.Agreement, SessionLocal()))
    

def pe_job():
    repo : GenericRepository = CreateRepo(models.Agreement, SessionLocal())
    agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
    repo2 : GenericRepository = CreateRepo(models.Client, SessionLocal())
    for agreement in agr:
        cli = repo2.get_by_condition(models.Client.client_id==agreement.client_id)
    send_to_origination(agr, cli)

scheduler = BackgroundScheduler()
scheduler.add_job(pe_job, 'interval', minutes=15)