from sqlalchemy import Column, Integer, String, DateTime
from common.models.base import Base

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