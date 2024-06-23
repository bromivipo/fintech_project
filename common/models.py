from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Double, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table
import datetime
import json

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "product"

    product_id = Column(String, primary_key=True)
    product_name = Column(String)
    product_version = Column(String)
    min_term = Column(Integer)
    max_term = Column(Integer)
    min_principle_amount = Column(Integer)
    max_principle_amount = Column(Integer)
    min_interest = Column(Double)
    max_interest = Column(Double)
    min_origination_amount = Column(Integer)
    max_origination_amount = Column(Integer)

    def __init__(self, prod: dict):
        self.product_id = prod["product_id"]
        self.product_name = prod["product_name"]
        self.product_version = prod["product_version"]
        self.min_term = prod["min_term"]
        self.max_term = prod["max_term"]
        self.min_principle_amount = prod["min_principle_amount"]
        self.max_principle_amount = prod["max_principle_amount"]
        self.min_interest = prod["min_interest"]
        self.max_interest = prod["max_interest"]
        self.min_origination_amount = prod["min_origination_amount"]
        self.max_origination_amount = prod["max_origination_amount"]


class Client(Base):
    __tablename__ = "client"

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String)
    birthday = Column(DateTime)
    email = Column(String)
    phone_number = Column(String)
    passport_details = Column(String)
    income = Column(Integer)

    def __init__(self, client):
        self.full_name = client["full_name"]
        self.birthday = client["birthday"]
        self.email = client["email"]
        self.phone_number = client["phone_number"]
        self.passport_details = client["passport_details"]
        self.income = client["income"]

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "client_id": self.client_id,
            "birthday": self.birthday,
            "email": self.email,
            "phone_number": self.phone_number,
            "passport_details": self.passport_details,
            "income": self.income
        }

class Agreement(Base):

    __tablename__ = "agreement"

    agreement_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String)
    client_id = Column(Integer)
    term = Column(Integer)
    principle_amount = Column(Double)
    interest = Column(Double)
    origination_amount = Column(Double)
    agreement_date = Column(DateTime)
    agreement_status = Column(String)

    def __init__(self, agreement):
        self.product_id = agreement["product_id"]
        self.client_id = agreement["client_id"]
        self.term = agreement["term"]
        self.principle_amount = agreement["principle_amount"]
        self.interest = agreement["interest"]
        self.origination_amount = agreement["origination_amount"]
        self.agreement_date = datetime.datetime.now()
        self.agreement_status = "NEW"
    
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "client_id": self.client_id,
            "term": self.term,
            "principle_amount": self.principle_amount,
            "interest": self.interest,
            "origination_amount": self.origination_amount,
            "agreement_date": self.agreement_date,
            "agreement_status": self.agreement_status
        }

class Application(Base):
    __tablename__ = "application"

    application_id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer)
    product_id = Column(String)
    client_id = Column(Integer)
    term = Column(Integer)
    principle_amount = Column(Double)
    interest = Column(Double)
    origination_amount = Column(Double)
    agreement_date = Column(DateTime)
    agreement_status = Column(String)

    def __init__(self, agreement):
        self.agreement_id = agreement["agreement_id"]
        self.product_id = agreement["product_id"]
        self.client_id = agreement["client_id"]
        self.term = agreement["term"]
        self.principle_amount = agreement["principle_amount"]
        self.interest = agreement["interest"]
        self.origination_amount = agreement["origination_amount"]
        self.agreement_date = datetime.datetime.now()
        self.agreement_status = "NEW"

class SchedulePayment(Base):

    __tablename__ = "schedule_payment"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer)
    expected_payment_date = Column(DateTime)
    principal_payment = Column(Double)
    interest_payment = Column(Double)
    period = Column(Integer)
    payment_status = Column(String)

    def __init__(self, schedule):
        self.agreement_id = schedule["agreement_id"]
        self.expected_payment_date = schedule["expected_payment_date"]
        self.principal_payment = schedule["principal_payment"]
        self.interest_payment = schedule["interest_payment"]
        self.period = schedule["period"]
        self.payment_status = schedule["payment_status"]
