
from core.database import SessionLocal
from models.user import User
from core.security import verify_password

def test_login(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found")
            return
        
        match = verify_password(password, user.password_hash)
        print(f"User: {username}")
        print(f"Hashed Password in DB: {user.password_hash}")
        print(f"Password Provided: {password}")
        print(f"Match: {match}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing admin login:")
    test_login("admin", "Admin@2024")
    print("\nTesting manager01 login:")
    test_login("manager01", "Manager@2024")
    print("\nTesting tech01 login:")
    test_login("tech01", "Tech@2024")