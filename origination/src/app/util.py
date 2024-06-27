import json
from common import models
from common.generic_repo import GenericRepository


def add_product(data, repo: GenericRepository):
    ints = ['min_term', 'max_term', 'min_principle_amount', 'max_principle_amount', 'min_origination_amount', 'max_origination_amount']
    doubles = ['min_interest', 'max_interest']
    new_product = json.loads(data)
    for field in ints:
        try:
            new_product[field] = int(new_product[field])
        except ValueError:
            return 400
    for field in doubles:
        try:
            new_product[field] = float(new_product[field])
        except ValueError:
            return 400
    new_product = models.Product(new_product)
    if repo.check_by_condition(models.Product.product_id == new_product.product_id \
                                or (models.Product.product_name == new_product.product_name and models.Product.product_version == new_product.product_version)) is not None:
        return 409
    else:
        repo.add(new_product)
        return 200


def create_application(repo: GenericRepository, data):
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

    new_application = models.Application(agreement)
    ans = check_application(repo, new_application)
    return ans


def check_application(repo: GenericRepository, new_application: models.Application):
    agr = repo.check_by_condition(models.Application.agreement_id == new_application.agreement_id)
    if agr is None:
        repo.add(new_application)
        return new_application.application_id
    else:
        return -1

def check_and_close_application(repo: GenericRepository, application_id):
    agr = repo.check_by_condition(models.Application.application_id == application_id)
    if agr is None:
        return False
    repo.update_by_condition(models.Application.application_id == application_id, "agreement_status", "CLOSED")
    return True


def set_application_status(repo: GenericRepository, msg):
    msg_from_topic = json.loads(msg)
    agr_id = msg_from_topic["agreement_id"]
    status = msg_from_topic["result_status"]
    repo.update_by_condition(models.Application.agreement_id==agr_id, "agreement_status", status)
