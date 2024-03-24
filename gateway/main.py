from fastapi import FastAPI, HTTPException
import requests
import json

app = FastAPI()

@app.get("/product", summary="Get a list of products")
def read_products():
    r = requests.get("http://127.0.0.1:8000/product")
    return r.json()

@app.get("/product/{product_code}", summary="Get product by id")
def get_product(product_code: str):
    r = requests.get(f"http://127.0.0.1:8000/product/{product_code}")
    return r.json()

@app.post("/agreement", summary="Post agreement, json with params of agreement should be forwarded")
def post_agr(d):
    headers = {"Content-Type": "application/json"}
    r = requests.post("http://127.0.0.1:8000/agreement", headers=headers, params={"d": d})
    return r.json()
