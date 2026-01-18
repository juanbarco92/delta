import logging
import sys
from sqlmodel import Session, select
from src.app.core.db import engine
from src.app.models.user import User
from src.app.models.credential import MeliCredential
from src.app.services.sync import sync_user_items

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

def main():
    with Session(engine) as session:
        # Get user
        user = session.exec(select(User).join(MeliCredential).limit(1)).first()
        if not user:
            print("No user found.")
            return

        print(f"Debugging Sync for user {user.id} ({user.meli_user_id})...")
        
        try:
            sync_user_items(user.id, session)
            print("Sync function completed.")
        except Exception as e:
            print(f"Sync failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
