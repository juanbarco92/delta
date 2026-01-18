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
            logger.error(f"HTTP Error: {e}")
            if e.response is not None:
                logger.error(f"Response body: {e.response.text}")

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

    def get_items_ids(self, user_id: int) -> list[str]:
        """
        Fetch all item IDs for a user.
        Uses the search endpoint to retrieve IDs.
        """
        # Initially, we only get 'results' which is a list of IDs.
        # Pagination might be needed if user has many items, but for now we implement basic search.
        # MeLi default limit is 50. We should scroll if more are needed.
        # For this ticket's scope, we'll implement simple scrolling.
        items = []
        offset = 0
        limit = 50
        while True:
            response = self._request("GET", f"/users/{user_id}/items/search", params={
                "search_type": "scan",
                "limit": limit,
                "offset": offset
            })
            results = response.get("results", [])
            items.extend(results)
            
            # Helper paging: if results < limit, we are done
            # Note: /users/{id}/items/search with search_type=scan is recommended for getting all items.
            # It uses scroll_id usually, but simple offset/limit works for standard search. 
            # For 'scan' type, MeLi returns scroll_id. Let's stick to standard search for simplicity unless 'scan' is strictly required.
            # Actually, the requirement says "GET /users/{id}/items/search".
            # Let's assume standard paging for now.
            paging = response.get("paging", {})
            total = paging.get("total", 0)
            
            if len(items) >= total or len(results) == 0:
                break
            
            offset += limit
            
        return items

    def get_items_details(self, ids: list[str]) -> list[Dict[str, Any]]:
        """
        Fetch item details for a list of IDs.
        Chunks requests in groups of 20 (MeLi limit for multiget).
        """
        chunk_size = 20
        all_details = []
        
        for i in range(0, len(ids), chunk_size):
            chunk = ids[i:i + chunk_size]
            ids_str = ",".join(chunk)
            response = self._request("GET", f"/items", params={"ids": ids_str})
            # Multi-get returns a list of results inside the response list (or sometimes dict with body).
            # The structure is list of objects with 'code' and 'body'.
            # Example response: [{ "code": 200, "body": { ... } }, { "code": 404, "body": ... }]
            if isinstance(response, list):
                for item_resp in response:
                    if item_resp.get("code") == 200:
                        all_details.append(item_resp.get("body"))
                    else:
                        logger.warning(f"Failed to fetch item details: {item_resp}")
            else:
                 # Should be a list usually for multiget
                 pass

        return all_details
