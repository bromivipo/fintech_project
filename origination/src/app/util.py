import json
from common.models.application import Application
from common.generic_repo import GenericRepository
from common.database import SessionLocal

def create_application(data):
    info = json.loads(data)
    agreement = {}
    agreement["agreement_id"] = info["agreement_id"]
    with open("logs.txt", "a") as file:
        file.write(f"agreement_id = {agreement['agreement_id']}")
    agreement["client_id"] = info["client_id"]
    agreement["term"] = info["term"]
    agreement["interest"] = info["interest"]
    agreement["origination_amount"] = info["origination_amount"]
    agreement["principle_amount"] =info["principle_amount"]
    agreement["product_id"] = info["product_id"]
    agreement["agreement_status"] = "NEW"

    new_application = Application(agreement)
    db = SessionLocal()
    repo = GenericRepository(db, Application)
    ans = check_application(repo, new_application)
    return ans


def check_application(repo: GenericRepository, new_application: Application):
    agr = repo.check_by_condition(Application.agreement_id == new_application.agreement_id)
    if agr is None:
        repo.add(new_application)
        return new_application.application_id
    else:
        return -1

def check_and_close_application(repo: GenericRepository, application_id):
    agr = repo.check_by_condition(Application.application_id == application_id)
    if agr is None:
        return False
    repo.update_by_condition(Application.application_id == application_id, "agreement_status", "CLOSED")
    return True


def set_application_status(msg):
    db = SessionLocal()
    repo = GenericRepository(db, Application)
    msg_from_topic = json.loads(msg)
    agr_id = msg_from_topic["agreement_id"]
    status = msg_from_topic["result_status"]
    repo.update_by_condition(Application.agreement_id==agr_id, "agreement_status", status)
