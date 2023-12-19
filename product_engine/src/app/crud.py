from sqlalchemy.orm import Session
from database import SessionLocal
import json
import datetime
import models
import random

class GenericRepository:

    def __init__(self, db:Session, entity:object):
        self.db = db
        self.entity = entity

    def get_all(self):
        return self.db.query(self.entity).all()
           
    def get_by_product_id(self, id):
        return self.db.query(self.entity).filter(self.entity.product_id==id).first()

    def check_product(self, id, name, version):
        return self.db.query(self.entity).filter(self.entity.product_id == id or \
                                      (self.entity.product_name == name and \
                                       self.entity.product_version == version)).first()

    def check_client(self, data):
        return self.db.query(self.entity).filter(self.entity.birthday == data["birthday"] and self.entity.email == data["email"] and \
                                    self.entity.full_name == data["full_name"] and self.entity.passport_details == data["passport_details"] and \
                                    self.entity.phone_number == data["phone_number"] and self.entity.income == data["income"]).first()

    def add(self, entity):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

    def delete_product(self, id):
        self.db.query(self.entity).filter(self.entity.product_id==id).delete()
        self.db.commit()


def get_products(db: Session):
    repo = GenericRepository(db, models.Product)
    return repo.get_all()

def get_product_by_code(db: Session, product_id: str):
    repo = GenericRepository(db, models.Product)
    return repo.get_by_product_id(product_id)

def add_product(db: Session, data):
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
    repo = GenericRepository(db, models.Product)
    
    if repo.check_product(new_product.product_id, new_product.product_name, new_product.product_version) is not None:
        return 409
    else:
        repo.add(new_product)
        return 200


def delete_product_by_code(db: Session, product_id: str):
    repo = GenericRepository(db, models.Product)
    repo.delete_product(product_id)

def create_agreement(db: Session, data):
    info = json.loads(data)
    client = {}
    agreement = {}
    client["full_name"] = info["first_name"] + " " + info["second_name"] + " " + info["third_name"]
    client["passport_details"] = info["passport_number"]
    client["email"] = info["email"]
    client["phone_number"] = info["phone"]
    repo = GenericRepository(db, models.Product)
    prod = repo.get_by_product_id(info["product_code"])

    if prod is None:
        return 0

    try:
        client["income"] = int(info["salary"])
        client["birthday"] = datetime.datetime.strptime(str(info["birthday"]), "%d.%m.%Y").strftime("%d.%m.%Y")
        agreement["term"] = int(info["term"])
        agreement["interest"] = float(info["interest"])
        agreement["origination_amount"] = float(random.randint(prod.min_origination_amount, prod.max_origination_amount))
        agreement["principle_amount"] = float(info["disbursment_amount"]) + agreement["origination_amount"]
    except ValueError:
        return -1

    if agreement["term"] > prod.max_term or agreement["term"] < prod.min_term:
        return -2
    
    if agreement["interest"] > prod.max_interest or agreement["interest"] < prod.min_term:
        return -3
    
    if agreement["principle_amount"] > prod.max_principle_amount or agreement["principle_amount"] < prod.min_principle_amount:
        return -4
    
    client = check_client(db, client)
    agreement["client_id"] = int(client)
    agreement["product_id"] = str(info["product_code"]) 

    new_agr = models.Agreement(agreement)
    repo2 = GenericRepository(db, models.Agreement)
    repo2.add(new_agr)
    return new_agr.agreement_id


def check_client(db: Session, data):
    repo = GenericRepository(db, models.Client)
    client = repo.check_client(data)
    if client is None:
        new = models.Client(data)
        repo.add(new)

        return new.client_id
    else:
        return client.client_id