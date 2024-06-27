import json
import datetime
from common.models.client import Client
from common.models.agreement import Agreement
from common.models.product import Product
from common.models.schedule_payment import SchedulePayment
from common.generic_repo import GenericRepository
from common.schemas import MsgPaymentReceived
from common.database import SessionLocal
import random
import numpy_financial as npf
import datetime
from dateutil.relativedelta import relativedelta


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
    new_product = Product(new_product)
    if repo.check_by_condition((Product.product_id == new_product.product_id) \
                                | (Product.product_name == new_product.product_name) & (Product.product_version == new_product.product_version)) is not None:
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
    if len(client["full_name"]) > 100 or len(client["email"]) > 100 or len(client["passport_details"]) > 20 or len(client["phone_number"]) > 20:
        return -5, None
    prod = repo.get_by_condition(Product.product_id == info["product_code"])
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

    new_agr = Agreement(agreement)
    repo2.add(new_agr)
    return 200, new_agr


def check_client(repo: GenericRepository, data):
    client = repo.check_by_condition(Client.passport_details == data["passport_details"])
    if client is None:
        new = Client(data)
        repo.add(new)

        return new.client_id
    else:
        return client.client_id

def update_status_new(ids, repo: GenericRepository):
    for id in ids:
        repo.update_by_condition(Agreement.agreement_id == id, "agreement_status", "SENT_TO_ORIGINATION")

def add_schedule_payment(msg):
    msg = json.loads(msg)
    db = SessionLocal()
    repo_payment = GenericRepository(db, SchedulePayment)
    repo_agr = GenericRepository(db, Agreement)
    if msg["result_status"] != "CLOSED":
        agr: Agreement = repo_agr.get_by_condition(Agreement.agreement_id == msg["agreement_id"])[0]
        repo_agr.update_by_condition(Agreement.agreement_id == msg["agreement_id"], "agreement_status", "ACTIVE")
        schedule_list = payment_schedule(agr.principle_amount, agr.interest, agr.term, agr.agreement_date)
        for schedule in schedule_list:
            data = schedule
            data["agreement_id"] = agr.agreement_id
            data["payment_status"] = "FUTURE"
            payment = SchedulePayment(data)
            repo_payment.add(payment)
    else:
        repo_agr.update_by_condition(Agreement.agreement_id == msg["agreement_id"], "agreement_status", "CLOSED")

def payment_schedule(principal, interest, term, start_date):
    monthly_interest_rate = interest / 12 / 100
    periods = range(1, term + 1)
    payment_schedule = []
    for period in periods:
        payment_date = start_date + relativedelta(months=period)
        principal_payment = npf.ppmt(monthly_interest_rate, period, term, -principal).round(2)
        interest_payment = npf.ipmt(monthly_interest_rate, period, term, -principal).round(2)
        payment_schedule.append({
            'expected_payment_date': payment_date,
            'principal_payment': float(principal_payment),
            'interest_payment': float(interest_payment),
            'period': period
        })
    
    return payment_schedule

def receive_payment(msg):
    db = SessionLocal()
    repo = GenericRepository(db, SchedulePayment)
    msg = json.loads(msg)
    payment_date = datetime.datetime.fromisoformat(msg["date"])
    payments = repo.get_by_condition((SchedulePayment.agreement_id==msg["agreement_id"]) & (SchedulePayment.payment_status=="FUTURE"))
    for payment in payments:
        if payment_date <= payment.expected_payment_date:
            if abs(msg["payment"] - payment.principal_payment - payment.interest_payment) < 0.001:
                repo.update_by_condition(SchedulePayment.payment_id==payment.payment_id, "payment_status", "PAID")
            break


