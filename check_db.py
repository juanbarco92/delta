from sqlmodel import select, Session
from src.app.core.db import engine
from src.app.models.user import User
from src.app.models.credential import MeliCredential

def check_data():
    with Session(engine) as session:
        print("-" * 30)
        print("USERS:")
        users = session.exec(select(User)).all()
        for user in users:
            print(user)
        
        print("-" * 30)
        print("CREDENTIALS:")
        creds = session.exec(select(MeliCredential)).all()
        for cred in creds:
            print(cred)
        print("-" * 30)

if __name__ == "__main__":
    check_data()
