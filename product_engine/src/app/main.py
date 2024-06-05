from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import CreateRepo, GenericRepository
from util import add_product, create_agreement
from common import models
from common.database import SessionLocal, engine
from common.schemas import MsgToOrigination
import os
import uvicorn
import json
from aiokafka import AIOKafkaProducer
from job import scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

KAFKA_INSTANCE = "kafka:29092"
topic = "new-agreements"

@app.on_event("startup")
async def startup_event():
    app.state.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_INSTANCE)
    await app.state.producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.producer.stop()

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
async def post_agreement(d, repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal())), repo2: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal())),  repo3: GenericRepository = Depends(CreateRepo(models.Client, SessionLocal()))):
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
    await app.state.producer.send_and_wait("new-agreements", json.dumps(msg.dict()).encode("ascii"))
    return agreement.agreement_id


if __name__ == '__main__':
    scheduler.start()
    uvicorn.run(app, port=os.getenv("PORT"), host=os.getenv("HOST"))