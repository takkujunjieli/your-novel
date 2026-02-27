from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel
from core.config import settings

# In SQLite, "check_same_thread" needs to be False for FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# Create the engine that will talk to the database
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# This function creates the tables in the database (we will call this on startup)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# This is our dependency that we will inject into our API endpoints
def get_session():
    with Session(engine) as session:
        yield session

# Create an Annotated type alias for cleaner code in our endpoints
# As per the FastAPI skill guide, this is a highly recommended best practice
SessionDep = Annotated[Session, Depends(get_session)]
