from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import GenericRepository
from util import add_product, create_agreement, add_schedule_payment, receive_payment
from common.models.client import Client
from common.models.agreement import Agreement
from common.models.product import Product
from common.models.base import Base
from common.models.schedule_payment import SchedulePayment
from common.database import engine, get_db
from common.schemas import MsgToOrigination
from common.kafka_common import consume, get_producer
from job import start_scheduler
import os
import uvicorn
import json
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/product", summary="Get a list of products")
def read_products(db = Depends(get_db)):
    repo = GenericRepository(db, Product)
    prod = repo.get_all()
    return prod


@app.get("/product/{product_id}", summary="Get a certain product by id")
def read_product(product_id: str, db = Depends(get_db)):
    repo = GenericRepository(db, Product)
    db_product = repo.get_by_condition(Product.product_id==product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.post("/product", summary="Add a new product")
def post_product(data, db = Depends(get_db)):
    repo = GenericRepository(db, Product)
    status = add_product(data, repo)
    if status == 400:
        raise HTTPException(status_code=400, detail="Wrong data types")
    if status == 409:
        raise HTTPException(status_code=409, detail="Product with given id or given name+version already exists")


@app.delete("/product/{product_id}", summary="Delete a certain product by id", status_code=204)
def delete_product(product_id: str, db = Depends(get_db)):
    repo = GenericRepository(db, Product)
    db_product = repo.delete_by_condition(Product.product_id==product_id)
    return db_product

@app.post("/agreement")
async def post_agreement(d,
                         db = Depends(get_db),
                         producer = Depends(get_producer)):
    repo = GenericRepository(db, Product)
    repo2 = GenericRepository(db, Agreement)
    repo3 = GenericRepository(db, Client) 
    errors = ["No product with a given code",
              "Wrong data types",
              "Term is out of range",
              "Interest is out of range",
              "Principle amount is out of range",
              "Personal data is too long: email and full name len must be <= 100, passport details and phone number len <= 20"]
    err, agreement = create_agreement(repo, repo2, repo3, d)
    if err <= 0:
        raise HTTPException(status_code=400, detail=errors[-err])
    msg = MsgToOrigination(
        name="kafka produce",
        agreement_id=agreement.agreement_id,
        product_id=agreement.product_id,
        client_id=agreement.client_id,
        term=agreement.term,
        principle_amount=agreement.principle_amount,
        interest=agreement.interest,
        origination_amount=agreement.origination_amount
        )
    await producer.send_and_wait(os.getenv("TOPIC_AGREEMENTS"), json.dumps(msg.dict()).encode("ascii"))
    return agreement.agreement_id

@app.get("/client_agreements", summary="All agreements for the client")
def clients_agreements(client_id: int, db = Depends(get_db)):
    repo = GenericRepository(db, Agreement)
    return repo.get_by_condition(Agreement.client_id==client_id)

@app.get("/schedule_for_agreement")
def schedule_for_agr(agr_id, db = Depends(get_db)):
    repo = GenericRepository(db, SchedulePayment)
    return repo.get_by_condition((SchedulePayment.agreement_id==agr_id) & (SchedulePayment.payment_status!="PAID"))

if __name__ == '__main__':
    with open("logs.txt", "a") as file:
        file.write(f"Started\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_scheduler())
    loop.create_task(consume(os.getenv("TOPIC_SCORING_RESPONSE"), "pe1",
                             add_schedule_payment))
    loop.create_task(consume(os.getenv("TOPIC_PAYMENT_RECEIVED"), "pe2",
                             receive_payment))
    
    config = uvicorn.Config(
        app=app,
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        loop=loop
    )
    server = uvicorn.Server(config)
    server_task = asyncio.ensure_future(server.serve())
    loop.run_until_complete(server_task)

    loop.close()