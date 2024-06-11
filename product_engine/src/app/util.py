import json
import datetime
from common import models
from common.generic_repo import GenericRepository
import random

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


def create_agreement(repo: GenericRepository, repo2: GenericRepository, repo3: GenericRepository, data):
    info = json.loads(data)
    client = {}
    agreement = {}
    client["full_name"] = info["first_name"] + " " + info["second_name"] + " " + info["third_name"]
    client["passport_details"] = info["passport_number"]
    client["email"] = info["email"]
    client["phone_number"] = info["phone"]
    prod = repo.get_by_condition(models.Product.product_id == info["product_code"])
    if len(prod) == 0:
        return 0
    prod = prod[0]
    try:
        client["income"] = int(info["salary"])
        client["birthday"] = datetime.datetime.strptime(str(info["birthday"]), "%d.%m.%Y").strftime("%d.%m.%Y")
        agreement["term"] = int(info["term"])
        agreement["interest"] = float(info["interest"])
        agreement["origination_amount"] = float(random.randint(prod.min_origination_amount, prod.max_origination_amount))
        agreement["principle_amount"] = float(info["disbursment_amount"]) + agreement["origination_amount"]
    except ValueError:
        return -1, None

    if agreement["term"] > prod.max_term or agreement["term"] < prod.min_term:
        return -2, None
    
    if agreement["interest"] > prod.max_interest or agreement["interest"] < prod.min_term:
        return -3, None
    
    if agreement["principle_amount"] > prod.max_principle_amount or agreement["principle_amount"] < prod.min_principle_amount:
        return -4, None
    
    client = check_client(repo3, client)
    agreement["client_id"] = int(client)
    agreement["product_id"] = str(info["product_code"]) 
    agreement['agreement_status'] = "NEW"

    new_agr = models.Agreement(agreement)
    repo2.add(new_agr)
    return 200, new_agr


def check_client(repo: GenericRepository, data):
    client = repo.check_by_condition(models.Client.passport_details == data["passport_details"])
    if client is None:
        new = models.Client(data)
        repo.add(new)

        return new.client_id
    else:
        return client.client_id

def update_status_new(ids, repo: GenericRepository):
    for id in ids:
        repo.update_by_condition(models.Agreement.agreement_id == id, "agreement_status", "SENT_TO_ORIGINATION")