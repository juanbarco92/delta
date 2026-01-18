import logging
from sqlmodel import Session, select
from src.app.models.user import User
from src.app.models.credential import MeliCredential
from src.app.models.item import Item
from src.meli_auditor.client import MeliClient
from src.meli_auditor.auth import MeliAuth

logger = logging.getLogger(__name__)

class DBMeliAuth(MeliAuth):
    """
    Adapter to use Database for token storage instead of local file.
    """
    def __init__(self, session: Session, credential: MeliCredential):
        # Skip super().__init__ to avoid loading from file which might not exist or be wrong
        self.access_token = credential.access_token
        self.refresh_token = credential.refresh_token
        self.expires_at = credential.expires_at
        
        self.db_session = session
        self.credential = credential

    def _save_tokens(self) -> None:
        """
        Override to save tokens to the database.
        """
        logger.info("Refreshing tokens in Database...")
        self.credential.access_token = self.access_token
        self.credential.refresh_token = self.refresh_token
        self.credential.expires_at = self.expires_at
        
        self.db_session.add(self.credential)
        self.db_session.commit()
        self.db_session.refresh(self.credential)
        logger.info("Tokens updated in DB.")

    def _load_tokens(self) -> None:
        # Already loaded in __init__
        pass

def sync_user_items(user_id: int, session: Session):
    """
    Synchronizes user items from Mercado Libre to the local database.
    """
    logger.info(f"Starting item sync for user_id={user_id}")
    
    # 1. Get Credential
    credential = session.exec(select(MeliCredential).where(MeliCredential.user_id == user_id)).first()
    if not credential:
        logger.error(f"No credentials found for user_id={user_id}")
        return

    # 2. Setup Client with DB Auth
    auth_adapter = DBMeliAuth(session, credential)
    client = MeliClient(auth=auth_adapter)

    try:
        # 3. Fetch all Item IDs
        # We need the User model to get the meli_user_id.
        user = session.get(User, user_id)
        if not user:
            logger.error(f"User not found for user_id={user_id}")
            return
            
        # The client.get_items_ids actually expects the MeLi User ID (numeric usually).
        # client.py says: get_items_ids(user_id: int). 
        # The URL is /users/{user_id}/items/search. This implies MeLi user ID.
        meli_user_id = user.meli_user_id
        
        logger.info(f"Fetching items for MeLi User ID: {meli_user_id}")
        item_ids = client.get_items_ids(meli_user_id)
        logger.info(f"Found {len(item_ids)} items.")
        
        if not item_ids:
            return

        # 4. Fetch Details
        # The client handles chunking internally now.
        items_details = client.get_items_details(item_ids)
        
        # 5. Upsert Items
        count = 0
        for details in items_details:
            # We map the details to our Item model
            item_data = {
                "id": details.get("id"),
                "user_id": user_id,
                "title": details.get("title"),
                "price": details.get("price"),
                "permalink": details.get("permalink"),
                "thumbnail": details.get("thumbnail"),
                "status": details.get("status"),
                "official_store_id": details.get("official_store_id"),
                # dimensions is inside 'shipping' -> 'dimensions' usually, or separate?
                # Actually, MeLi 'dimensions' field is often null at top level, sometimes in shipping.
                # Let's check a standard response structure or just safely get it.
                # Common field is 'shipping.dimensions'.
                "dimensions": details.get("shipping", {}).get("dimensions")
            }
            
            # Use upsert logic
            existing_item = session.get(Item, item_data["id"])
            if existing_item:
                for k, v in item_data.items():
                    setattr(existing_item, k, v)
                session.add(existing_item)
            else:
                new_item = Item(**item_data)
                session.add(new_item)
            
            count += 1
        
        session.commit()
        logger.info(f"Successfully synced {count} items for user_id={user_id}")

    except Exception as e:
        logger.error(f"Error syncing items for user_id={user_id}: {e}")
        # Optionally re-raise if we want the background task to fail visibly, but usually logging is enough for async workers
