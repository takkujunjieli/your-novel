from fastapi import APIRouter

# As per the FastAPI skill guide, we add prefix and tags directly to the router
router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Your Novel API",
        "version": "1.0.0"
    }
