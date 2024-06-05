from pydantic import BaseModel, StrictStr

class MsgToOrigination(BaseModel):
    name: StrictStr
    agreement_id: int
    product_id: StrictStr
    client_id: int
    term: int
    principle_amount: float
    interest: float
    origination_amount: float