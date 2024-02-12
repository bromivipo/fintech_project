from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from crud import create_repo, GenericRepository, create_agreement, check_and_delete_agr
import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/application", summary="Create an application, agreement + client info should be provided in json")
def post_app(data, repo: GenericRepository = Depends(create_repo(models.Client)), repo2: GenericRepository = Depends(create_repo(models.Agreement))):
    application = create_agreement(repo, repo2, data)
    if (application == -1):
        raise HTTPException(status_code=409, detail="Application already exists")
    return application


@app.post("/application/{application_id}/close", summary="Close application. application_id = agreement_id")
def delete_app(application_id, repo: GenericRepository = Depends(create_repo(models.Agreement))):
    status = check_and_delete_agr(repo, application_id)
    if not status:
        raise HTTPException(status_code=404, detail="Application not found")