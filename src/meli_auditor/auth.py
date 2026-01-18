import json
import time
import requests
import logging
from typing import Optional, Dict, Any
from .config import settings

TOKEN_FILE = "tokens.json"
AUTH_URL = "https://auth.mercadolibre.com.co/authorization"
TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

logger = logging.getLogger(__name__)

class MeliAuth:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: float = 0
        self._load_tokens()

    def get_auth_url(self) -> str:
        return (
            f"{AUTH_URL}?response_type=code&client_id={settings.APP_ID}"
            f"&redirect_uri={settings.REDIRECT_URI}"
        )

    def exchange_code(self, code: str) -> Dict[str, Any]:
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.APP_ID,
            "client_secret": settings.CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.REDIRECT_URI,
        }
        return self._request_token(payload)

    def get_token(self) -> str:
        if not self.access_token:
            raise Exception("No access token available. Please authenticate first.")
        
        if time.time() > self.expires_at - 60:  # Refresh 60s before expiry
            self._refresh_token()
            
        return self.access_token

    def _refresh_token(self) -> None:
        if not self.refresh_token:
            raise Exception("No refresh token available.")

        payload = {
            "grant_type": "refresh_token",
            "client_id": settings.APP_ID,
            "client_secret": settings.CLIENT_SECRET,
            "refresh_token": self.refresh_token,
        }
        try:
            self._request_token(payload)
        except Exception as e:
            # If refresh fails, might be revoked.
            logger.error(f"Error refreshing token: {e}")
            raise

    def _request_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        # expires_in is seconds
        self.expires_at = time.time() + data["expires_in"]
        self._save_tokens()
        return data

    def _save_tokens(self) -> None:
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(data, f)

    def _load_tokens(self) -> None:
        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.expires_at = data.get("expires_at", 0)
        except FileNotFoundError:
            pass
