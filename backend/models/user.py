import uuid
from datetime import date, datetime
from typing import Optional, Any
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from pydantic import ConfigDict

# This is the base model for the User table
class UserBase(SQLModel):
    device_id: str = Field(unique=True, index=True)
    is_adult: bool = Field(default=False)
    # Explicitly mapping Python dictionaries to SQLAlchemy JSON columns
    preferences: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

# This represents the database table
class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    age_verified_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# This is what we will return to the frontend
class UserPublic(UserBase):
    id: uuid.UUID
    age_verified_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
