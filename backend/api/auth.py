from datetime import date
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

# We bring in our database session dependency and our User models
from core.db import SessionDep
from models.user import User, UserPublic

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# We define what the incoming JSON request should look like
from pydantic import BaseModel
class AgeVerificationRequest(BaseModel):
    device_id: str
    is_adult: bool

@router.post("/age-verify", response_model=UserPublic)
def verify_age(request: AgeVerificationRequest, session: SessionDep):
    # 1. Self-attestation check
    if not request.is_adult:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must confirm you are at least 18 years old to use this application."
        )

    # 2. Check if a user with this device_id already exists
    statement = select(User).where(User.device_id == request.device_id)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        return existing_user

    # 3. Create a new user
    new_user = User(
        device_id=request.device_id,
        is_adult=request.is_adult
    )
    
    # 4. Save to database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user
