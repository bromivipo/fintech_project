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


def create_agreement(repo: GenericRepository, repo2: GenericRepository, data):
    info = json.loads(data)
    client = {}
    agreement = {}
    client["client_id"] = info["client_id"]
    client["full_name"] = info["full_name"]
    client["passport_details"] = info["passport_number"]
    client["email"] = info["email"]
    client["phone_number"] = info["phone"]
    client["income"] = info["salary"]
    client["birthday"] = info["birthday"]
    agreement["term"] = info["term"]
    agreement["interest"] = info["interest"]
    agreement["origination_amount"] = info["origination_amount"]
    agreement["principle_amount"] =info["principle_amount"]
    client = check_client(repo, client)
    agreement["client_id"] = client
    agreement["product_id"] = info["product_id"]
    agreement["agreement_status"] = "NEW"

    new_agr = models.Agreement(agreement)
    ans = check_agr(repo2, new_agr)
    return ans


def check_client(repo: GenericRepository, data):
    client = repo.check_by_condition(models.Client.client_id == data["client_id"])
    if client is None:
        new = models.Client(data)
        repo.add(new)
        return new.client_id
    else:
        return client.client_id


def check_agr(repo: GenericRepository, new_agr: models.Agreement):
    agr = repo.check_by_condition(models.Agreement.agreement_id == new_agr.agreement_id)
    if agr is None:
        repo.add(new_agr)
        return new_agr.agreement_id
    else:
        return -1

def check_and_delete_agr(repo: GenericRepository, agr_id):
    agr = repo.check_by_condition(models.Agreement.agreement_id == agr_id)
    if agr is None:
        return False
    repo.delete_by_condition(models.Agreement.agreement_id == agr_id)
    return True
