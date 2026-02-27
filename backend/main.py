from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.health import router as health_router
from api.auth import router as auth_router
from core.db import create_db_and_tables
import models.user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create the database tables
    create_db_and_tables()
    yield
    # Code after 'yield' runs when the server shuts down (if any)

app = FastAPI(
    title="Your Novel API",
    description="Backend API for the AI-native adult content platform",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(auth_router)
