import requests
import sys
from sqlmodel import Session, select
from src.app.core.db import engine
from src.app.models.user import User
from src.app.models.credential import MeliCredential

def main():
    # 1. Get a valid user
    with Session(engine) as session:
        statement = select(User).join(MeliCredential).limit(1)
        user = session.exec(statement).first()
        
        if not user:
            print("No user with credentials found in DB. Cannot verify sync.")
            sys.exit(1)
            
        print(f"Found user: {user.email} (ID: {user.id})")
        user_id = user.id

    # 2. Trigger Sync Endpoint
    print(f"Triggering sync for user_id={user_id}...")
    try:
        response = requests.post(
            "http://localhost:8000/sync/items", 
            params={"user_id": user_id}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("Sync started successfully.")
        else:
            print("Failed to start sync.")
            
    except Exception as e:
        print(f"Error triggering sync: {e}")

if __name__ == "__main__":
    main()
