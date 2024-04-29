from fastapi import FastAPI, HTTPException
import requests
import uvicorn
import os

app = FastAPI()

@app.get("/product", summary="Get a list of products")
def read_products():
    r = requests.get("http://{}/product".format(os.getenv("PE_PATH")))  
    if r.status_code == 200: 
        return r.json()
    raise HTTPException(r.status_code)

@app.get("/product/{product_code}", summary="Get product by id")
def get_product(product_code: str):
    r = requests.get("http://{}/product/{}".format(os.getenv("PE_PATH"), product_code))
    if r.status_code == 200: 
        return r.json()
    raise HTTPException(r.status_code)


@app.post("/agreement", summary="""Post agreement, json with params of agreement should be forwarded(agreement_id, product_id, client_id, term, principle_amount, interest, origination_amount, agreement_date, agreement_status,""")
def post_agr(d):
    headers = {"Content-Type": "application/json"}
    r = requests.post("http://{}/agreement".format(os.getenv("PE_PATH")), headers=headers, params={"d": d})
    if r.status_code == 200: 
        return r.json()
    raise HTTPException(r.status_code)


if __name__ == '__main__':
    uvicorn.run(app, port=os.getenv("PORT"), host=os.getenv("HOST"))