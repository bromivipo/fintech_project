from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/product", summary="Get a list of products")
def read_products(db: Session = Depends(get_db)):
    users = crud.get_products(db)
    return users


@app.get("/product/{product_id}", summary="Get a certain product by id")
def read_product(product_id: str, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_code(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.post("/product", summary="Add a new product")
def post_product(data, db: Session = Depends(get_db)):
    status = crud.add_product(db, data)
    if status == 400:
        raise HTTPException(status_code=400, detail="Wrong data types")
    if status == 409:
        raise HTTPException(status_code=409, detail="Product with given id or given name+version already exists")


@app.delete("/product/{product_id}", summary="Delete a certain product by id", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = crud.delete_product_by_code(db, product_id=product_id)
    return db_product

@app.post("/agreement")
def post_agreement(data, db: Session = Depends(get_db)):
    errors = ["No product with a given code",
              "Wrong data types",
              "Term is out of range",
              "Interest is out of range",
              "Principle amount is out of range"]
    agreement = crud.create_agreement(db, data)
    if agreement <= 0:
        raise HTTPException(status_code=400, detail=errors[-agreement])
    return agreement