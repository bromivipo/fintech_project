from pydantic import BaseModel, StrictStr
from datetime import datetime

class MsgToOrigination(BaseModel):
    name: StrictStr
    agreement_id: int
    product_id: StrictStr
    client_id: int
    term: int
    principle_amount: float
    interest: float
    origination_amount: float

class MsgToScoring(BaseModel):
    name: StrictStr
    agreement_id: int
    product_id: StrictStr
    client_id: int

class MsgFromScoring(BaseModel):
    name: StrictStr
    agreement_id: int
    product_id: StrictStr
    client_id: int
    result_status: StrictStr

class MsgPaymentReceived(BaseModel):
    agreement_id: int
    date: datetime
    payment: float
