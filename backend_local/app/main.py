from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, workspace, synthesis

app = FastAPI(
    title="Archivision Studio API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(synthesis.router)

@app.get("/")
def root():
    return {
        "message": "Archivision Studio API",
        "status": "operational",
        "docs": "/docs"
    }
