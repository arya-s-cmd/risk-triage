from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
DB_URL=os.getenv('DB_URL','sqlite:///./risk.db')
engine=create_engine(DB_URL, future=True, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
