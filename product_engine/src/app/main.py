from fastapi import Depends, FastAPI, HTTPException
from common.generic_repo import CreateRepo, GenericRepository
from util import add_product, create_agreement
from common import models
from common.database import SessionLocal, engine
import os
import uvicorn
from job import scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
def post_agreement(d, repo: GenericRepository = Depends(CreateRepo(models.Product, SessionLocal())), repo2: GenericRepository = Depends(CreateRepo(models.Agreement, SessionLocal())),  repo3: GenericRepository = Depends(CreateRepo(models.Client, SessionLocal()))):
    errors = ["No product with a given code",
              "Wrong data types",
              "Term is out of range",
              "Interest is out of range",
              "Principle amount is out of range"]
    agreement = create_agreement(repo, repo2, repo3, d)
    if agreement <= 0:
        raise HTTPException(status_code=400, detail=errors[-agreement])
    return agreement


if __name__ == '__main__':
    scheduler.start()
    uvicorn.run(app, port=os.getenv("PORT"), host=os.getenv("HOST"))