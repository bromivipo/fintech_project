from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


engine = create_engine(os.getenv("ENGINE"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
