from sqlalchemy import Column, Integer, String, Double, DateTime
from common.models.base import Base
import datetime

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
        self.agreement_date = datetime.datetime.now(datetime.timezone.utc)
        self.agreement_status = "NEW"
    
    def to_dict(self):
        return {
            "agreement_id": self.agreement_id,
            "product_id": self.product_id,
            "client_id": self.client_id,
            "term": self.term,
            "principle_amount": self.principle_amount,
            "interest": self.interest,
            "origination_amount": self.origination_amount,
            "agreement_date": self.agreement_date,
            "agreement_status": self.agreement_status
        }