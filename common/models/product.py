from sqlalchemy import Column, Integer, String, Double
from common.models.base import Base

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