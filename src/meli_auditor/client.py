import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
import logging
from typing import Dict, Any, Optional

from .auth import MeliAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.mercadolibre.com"

class MeliClient:
    def __init__(self, auth: MeliAuth):
        self.auth = auth
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/json"
        }

    @retry(
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        url = f"{BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.request(method, url, headers=headers, params=params, json=data)
            
            if response.status_code == 429:
                # Handle rate limit specifically if needed, though tenacity can handle status codes if configured
                # For this PoC, we let it fail or could implement specific wait
                logger.warning("Rate limit hit. Retrying should be handled by caller or extended retry logic.")
                response.raise_for_status()

            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # Token might be expired/revoked, force refresh could be added here
                logger.error("Unauthorized. Token logic should handle auto-refresh.")
            raise

    def get_me(self) -> Dict[str, Any]:
        return self._request("GET", "/users/me")

    def get_orders(self, seller_id: int, limit: int = 50) -> Dict[str, Any]:
        # Sort by date_desc to get latest
        return self._request("GET", f"/orders/search", params={
            "seller": seller_id,
            "sort": "date_desc",
            "limit": limit
        })

    def get_shipment(self, shipment_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/shipments/{shipment_id}")
