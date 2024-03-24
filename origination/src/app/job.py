from apscheduler.schedulers.background import BackgroundScheduler
import time
from crud import create_repo, GenericRepository
import models
from database import SessionLocal

def send_to_scoring():
    #заглушка для скоринга
    pass

def orig_job():
    repo : GenericRepository = create_repo(models.Agreement)
    agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
    repo.update_by_condition(models.Agreement.agreement_status == "NEW", "agreement_status", "SCORING")
    send_to_scoring(agr)

scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(orig_job, 'interval', minutes=15)
