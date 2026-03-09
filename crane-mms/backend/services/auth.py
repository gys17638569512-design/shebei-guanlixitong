from sqlalchemy.orm import Session
from core.security import verify_password, create_access_token
from core.exceptions import UnauthorizedError
from repositories import user as user_repo

def login_user(db: Session, username: str, password: str) -> dict:
    usr = user_repo.get_user_by_username(db, username)
    if not usr or not verify_password(password, usr.password_hash):
        raise UnauthorizedError("Incorrect username or password")
    
    access_token = create_access_token(data={"sub": usr.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usr.id,
            "username": usr.username,
            "name": usr.name,
            "role": usr.role
        }
    }
