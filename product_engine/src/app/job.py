from apscheduler.schedulers.background import BackgroundScheduler
import time
from crud import create_repo, GenericRepository
import models
from database import SessionLocal

def send_to_origination(agr):
    #заглушка для origination, потому что пока compose все равно нет
    pass

def pe_job():
    repo : GenericRepository = create_repo(models.Agreement)
    agr = repo.get_by_condition(models.Agreement.agreement_status == "NEW")
    # добавил ручку в main для того, чтобы получать agreement_id которые уже попали в origination, подробнее в readme
    send_to_origination(agr)

scheduler = BackgroundScheduler()
scheduler.start()

scheduler.add_job(pe_job, 'interval', minutes=15)