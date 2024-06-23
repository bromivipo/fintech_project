from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import CreateRepo, GenericRepository
from util import add_product, create_agreement, add_schedule_payment
from common import models
from common.database import SessionLocal, engine
from common.schemas import MsgToOrigination
import os
import uvicorn
import json
import traceback
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

async def consume(topic, 
                  func, 
                  repo_payment=GenericRepository(SessionLocal(), models.SchedulePayment),
                  repo_agr=GenericRepository(SessionLocal(), models.Agreement)):
    consumer = AIOKafkaConsumer(
        topic,
        group_id="pe",
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        bootstrap_servers=os.getenv("KAFKA_INSTANCE"),
    )
    await consumer.start()
    try:
        async for message in consumer:
            with open("logs.txt", "a") as file:
                file.write(f"Received: {message.value.decode()}, topic: {message.topic}, offset: {message.offset}\n")
            func(repo_payment, repo_agr, message.value.decode())
    except Exception:
        with open("logs.txt", "a") as file:
            file.write(traceback.format_exc())
    finally:
        with open("logs.txt", "a") as file:
            file.write(f"Stopped")
        await consumer.stop()

async def get_producer():
    producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_INSTANCE"))
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()



@app.get("/product", summary="Get a list of products")
def read_products(repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal()))):
    prod = repo.get_all()
    return prod


@app.get("/product/{product_id}", summary="Get a certain product by id")
def read_product(product_id: str, repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal()))):
    db_product = repo.get_by_condition(models.Product.product_id==product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.post("/product", summary="Add a new product")
def post_product(data, repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal()))):
    status = add_product(data, repo)
    if status == 400:
        raise HTTPException(status_code=400, detail="Wrong data types")
    if status == 409:
        raise HTTPException(status_code=409, detail="Product with given id or given name+version already exists")


@app.delete("/product/{product_id}", summary="Delete a certain product by id", status_code=204)
def delete_product(product_id: str, repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal()))):
    db_product = repo.delete_by_condition(models.Product.product_id==product_id)
    return db_product

@app.post("/agreement")
async def post_agreement(d,
                         repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal())),
                         repo2: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal())),
                         repo3: GenericRepository = Depends(CreateRepo(models.Client, SessionLocal())),
                         producer = Depends(get_producer)):
    errors = ["No product with a given code",
              "Wrong data types",
              "Term is out of range",
              "Interest is out of range",
              "Principle amount is out of range"]
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

@app.get("/client_agreements", summary="All unclosed agreements for the client")
def clients_agreements(client_id: int, repo: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal()))):
    return repo.get_by_condition(models.Agreement.client_id==client_id)

if __name__ == '__main__':
    with open("logs.txt", "a") as file:
        file.write(f"Started\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(consume(os.getenv("TOPIC_SCORING_RESPONSE"),
                             add_schedule_payment))
    
    config = uvicorn.Config(
        app=app,
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        loop=loop
    )
    server = uvicorn.Server(config)
    server_task = asyncio.ensure_future(server.serve())
    loop.run_until_complete(server_task)