from apscheduler.schedulers.background import BackgroundScheduler
from common.generic_repo import CreateRepo, GenericRepository
from common import models
from common.database import SessionLocal
import requests

def send_to_scoring(agr):
    pass

def orig_job():
    repo : GenericRepository = CreateRepo(models.Agreement, SessionLocal())
    agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
    repo.update_by_condition(models.Agreement.agreement_status == "NEW", "agreement_status", "SCORING")
    send_to_scoring(agr)

scheduler = BackgroundScheduler()
scheduler.add_job(orig_job, 'interval', minutes=15)
