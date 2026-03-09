from sqlalchemy.orm import Session
from models.user import User

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    query = db.query(User)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items

def create_user(db: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    db.add(db_user)
    db.flush()
    return db_user

def update_user(db: Session, db_user: User, update_data: dict) -> User:
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.flush()
    return db_user

def delete_user(db: Session, db_user: User) -> bool:
    db.delete(db_user)
    db.flush()
    return True
