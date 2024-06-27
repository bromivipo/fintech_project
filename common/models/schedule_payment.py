from sqlalchemy import Column, Integer, String, Double, DateTime
from common.models.base import Base

class SchedulePayment(Base):

    __tablename__ = "schedule_payment"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    agreement_id = Column(Integer)
    expected_payment_date = Column(DateTime)
    principal_payment = Column(Double)
    interest_payment = Column(Double)
    total_payment = Column(Double)
    period = Column(Integer)
    payment_status = Column(String)

    def __init__(self, schedule):
        self.agreement_id = schedule["agreement_id"]
        self.expected_payment_date = schedule["expected_payment_date"]
        self.principal_payment = schedule["principal_payment"]
        self.interest_payment = schedule["interest_payment"]
        self.period = schedule["period"]
        self.payment_status = schedule["payment_status"]
        self.total_payment = round(self.principal_payment + self.interest_payment,2)
