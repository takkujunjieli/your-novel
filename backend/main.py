from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.health import router as health_router

app = FastAPI(
    title="Your Novel API",
    description="Backend API for the AI-native adult content platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
