from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


engine = create_engine(os.getenv("ENGINE"), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()