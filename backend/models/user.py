import uuid
from datetime import date, datetime
from typing import Optional, Any
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict

class UserBase(SQLModel):
    device_id: str = Field(unique=True, index=True)
    date_of_birth: date
    # In SQLite JSONB is not supported, so we will adapt this later for Postgres
    preferences: Optional[dict[str, Any]] = None

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
