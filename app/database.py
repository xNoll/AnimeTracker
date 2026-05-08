from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# Physical connection to the DB.
connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {} # check_same_thread has to be False for SQLite because it doesn't admit threads.
engine = create_engine(url=settings.database_url, connect_args=connect_args)

# Session-maker factory.
## A session is not the conection itself, it's the layer where operations occur.
SessionLocal = sessionmaker(
    autoflush=False,
    bind=engine,
    autocommit=False   
)

# Class that will inherit all our ORM models (Factory).
class Base(declarative_base):
    pass

# 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
