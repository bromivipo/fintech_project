from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from crud import create_repo, GenericRepository, add_product, create_agreement, update_status_new
import models
from database import SessionLocal, engine
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/product", summary="Get a list of products")
def read_products(repo: GenericRepository = Depends(create_repo(models.Product))):
    prod = repo.get_all()
    return prod


@app.get("/product/{product_id}", summary="Get a certain product by id")
def read_product(product_id: str, repo: GenericRepository = Depends(create_repo(models.Product))):
    db_product = repo.get_by_condition(models.Product.product_id==product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.post("/product", summary="Add a new product")
def post_product(data, repo: GenericRepository = Depends(create_repo(models.Product))):
    status = add_product(data, repo)
    if status == 400:
        raise HTTPException(status_code=400, detail="Wrong data types")
    if status == 409:
        raise HTTPException(status_code=409, detail="Product with given id or given name+version already exists")


@app.delete("/product/{product_id}", summary="Delete a certain product by id", status_code=204)
def delete_product(product_id: str, repo: GenericRepository = Depends(create_repo(models.Product))):
    db_product = repo.delete_by_condition(models.Product.product_id==product_id)
    return db_product

@app.post("/agreement")
def post_agreement(d, repo: GenericRepository = Depends(create_repo(models.Product)), repo2: GenericRepository = Depends(create_repo(models.Agreement)),  repo3: GenericRepository = Depends(create_repo(models.Client))):
    errors = ["No product with a given code",
              "Wrong data types",
              "Term is out of range",
              "Interest is out of range",
              "Principle amount is out of range"]
    agreement = create_agreement(repo, repo2, repo3, d)
    if agreement <= 0:
        raise HTTPException(status_code=400, detail=errors[-agreement])
    return agreement

@app.post("/origination_received_agreements")
def update_agr_status(ids, repo: GenericRepository = Depends(create_repo(models.Agreement))):
    ids = json.loads(ids)
    ids = ids["ids"]
    update_status_new(ids, repo)