import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.routers import (
    auth_router,
    events_router,
    registrations_router,
    users_router,
    dashboard_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed data on startup
    init_db()
    yield


app = FastAPI(
    title="Online Event Management System API",
    description="Backend API supporting authentication, event management, registrations, and dashboard reports.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_router.router)
app.include_router(events_router.router)
app.include_router(registrations_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)

# Mount Frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
