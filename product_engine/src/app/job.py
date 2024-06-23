# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from common.generic_repo import CreateRepo, GenericRepository
# from common.database import SessionLocal
# from common import models
# from util import update_status_new
# import requests
# import asyncio
# import os


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

# async def start_scheduler():
#     with open("logs.txt", "a") as file:
#         file.write(f"Started job\n")
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(pe_job, 'interval', seconds=10)
#     scheduler.start()
#     await asyncio.Event().wait()