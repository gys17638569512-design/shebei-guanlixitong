from sqlalchemy.orm import Session
from core.security import get_password_hash
from core.exceptions import BusinessError, NotFoundError
from repositories import user as user_repo
from schemas.user import UserCreate, UserUpdate

def get_users(db: Session, skip: int = 0, limit: int = 100):
    total, items = user_repo.get_users(db, skip=skip, limit=limit)
    return {"total": total, "items": items}

def get_user(db: Session, user_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("用户未找到")
    return user

def create_user(db: Session, user_in: UserCreate):
    # 检查用户名是否已存在
    if user_repo.get_user_by_username(db, user_in.username):
        raise BusinessError("该用户名已存在，请更换重试")
    
    user_data = user_in.model_dump()
    # 哈希密码
    password = user_data.pop("password")
    user_data["password_hash"] = get_password_hash(password)
    
    user = user_repo.create_user(db, user_data)
    db.commit()
    return user

def update_user(db: Session, user_id: int, user_in: UserUpdate):
    db_user = user_repo.get_user_by_id(db, user_id)
    if not db_user:
        raise NotFoundError("用户未找到")

    update_data = user_in.model_dump(exclude_unset=True)
    
    # 如果修改了用户名，需要检查是否与其他用户冲突
    if "username" in update_data and update_data["username"] != db_user.username:
        if user_repo.get_user_by_username(db, update_data["username"]):
            raise BusinessError("更新失败：该用户名已被其他账户使用")

    # 如果有新密码，进行哈希处理
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["password_hash"] = get_password_hash(password)

    user = user_repo.update_user(db, db_user, update_data)
    db.commit()
    return user

def delete_user(db: Session, user_id: int):
    # 防止删除默认 admin
    if user_id == 1:
        raise BusinessError("系统的初始超级管理员账户不允许被删除")
    
    db_user = user_repo.get_user_by_id(db, user_id)
    if not db_user:
        raise NotFoundError("用户未找到")
        
    user_repo.delete_user(db, db_user)
    db.commit()
    return True
