from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.app.routers import auth

app = FastAPI(title="MeLi Auditor API")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

def start():
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
