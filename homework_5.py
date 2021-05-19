import os
from fastapi import APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

router=APIRouter()

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

