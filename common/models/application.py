from sqlalchemy import Column, Integer, String, Double, DateTime
import datetime
from common.models.base import Base

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