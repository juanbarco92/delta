from sqlmodel import Session, select, func
from src.app.core.db import engine
from src.app.models.item import Item
from src.app.models.user import User

def main():
    with Session(engine) as session:
        # Get the same user
        user = session.exec(select(User).limit(1)).first()
        if not user:
            print("No user found.")
            return

        print(f"Checking items for user {user.id}...")
        
        # Count items
        statement = select(func.count()).select_from(Item).where(Item.user_id == user.id)
        count = session.exec(statement).one()
        
        print(f"Total items found: {count}")
        
        if count > 0:
            # Show a sample
            item = session.exec(select(Item).where(Item.user_id == user.id).limit(1)).first()
            print(f"Sample Item: {item.title} ({item.id}) - {item.price}")

if __name__ == "__main__":
    main()
