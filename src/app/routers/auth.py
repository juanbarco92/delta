from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, select
import requests
import time
from src.meli_auditor.auth import MeliAuth
from src.app.core.db import get_session
from src.app.models.user import User
from src.app.models.credential import MeliCredential

router = APIRouter()
auth_handler = MeliAuth()

@router.get("/login")
def login():
    """Redirects user to Mercado Libre OAuth login."""
    auth_url = auth_handler.get_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
def callback(code: str, session: Session = Depends(get_session)):
    """Callback from Mercado Libre with auth code."""
    try:
        tokens = auth_handler.exchange_code(code)
        
        meli_user_id = tokens.get("user_id")
        access_token = tokens.get("access_token")

        if not meli_user_id:
            raise Exception("No user_id in token response.")

        # Check if user exists
        user = session.exec(select(User).where(User.meli_user_id == meli_user_id)).first()
        
        if not user:
            # Fetch user email from MeLi
            headers = {"Authorization": f"Bearer {access_token}"}
            me_resp = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
            me_data = me_resp.json()
            email = me_data.get("email", f"missing_{meli_user_id}@example.com")
            
            user = User(email=email, meli_user_id=meli_user_id)
            session.add(user)
            session.commit()
            session.refresh(user)

        # Update or create credentials
        credential = session.exec(select(MeliCredential).where(MeliCredential.user_id == user.id)).first()
        expires_at = int(time.time() + tokens.get("expires_in", 21600)) # Default 6 hours if missing

        if credential:
            credential.access_token = tokens["access_token"]
            credential.refresh_token = tokens["refresh_token"]
            credential.expires_at = expires_at
            session.add(credential)
        else:
            credential = MeliCredential(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                expires_at=expires_at,
                user_id=user.id
            )
            session.add(credential)
        
        session.commit()

        return {"status": "success", "user_id": user.id, "meli_user_id": user.meli_user_id}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
