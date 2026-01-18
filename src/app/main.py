from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel
from src.app.routers import auth, sync
from src.app.core.db import engine
from src.app.models.user import User
from src.app.models.credential import MeliCredential
from src.app.models.item import Item # Import models to register them

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="MeLi Auditor API", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sync.router, prefix="/sync", tags=["Sync"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

def start():
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
