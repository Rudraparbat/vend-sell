from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os 
from dotenv import load_dotenv
load_dotenv()

# Defining Database url

DB_URL = os.getenv("DATABASE_URL")

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

# initilizing engine

engine = create_engine(DB_URL , connect_args=connect_args)

# initializing session

Sessions = sessionmaker(autoflush=False , autocommit = False , bind=engine)

# Initializing Base model 

Base = declarative_base()

def get_db():
    db = Sessions()
    try:
        yield db
    finally:
        db.close()