from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from src.meli_auditor.auth import MeliAuth

router = APIRouter()
auth_handler = MeliAuth()

@router.get("/login")
def login():
    """Redirects user to Mercado Libre OAuth login."""
    auth_url = auth_handler.get_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
def callback(code: str):
    """Callback from Mercado Libre with auth code."""
    try:
        tokens = auth_handler.exchange_code(code)
        return JSONResponse(content=tokens)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
