from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from services import user_service

router = APIRouter(prefix="/users", tags=["人员管理"])

@router.get("", summary="获取员工列表", description="分页查询系统中所有的员工账户信息，支持按角色过滤。ADMIN 可看全员，MANAGER 可看工程师列表用于派单。")
def get_users(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(100, description="每页返回的最大记录数量"),
    role: str = Query(None, description="按角色过滤，如 TECH/MANAGER/ADMIN"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    # 如果指定了 role 过滤，直接查询对应角色用户
    if role:
        from models.user import User as UserModel, RoleEnum
        users = db.query(UserModel).filter(UserModel.role == role).offset(skip).limit(limit).all()
        total = db.query(UserModel).filter(UserModel.role == role).count()
        return ok({"total": total, "items": users})
    data = user_service.get_users(db, skip=skip, limit=limit)
    return ok(data)

@router.get("/{id}", summary="获取员工详情", description="根据员工ID获取特定的员工资料。")
def get_user(
    id: int = Path(..., description="要查询的员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.get_user(db, id)
    return ok(data)

@router.post("", summary="创建新员工账号", description="录入新的系统使用者，自动使用 bcrypt 加盐哈希密码存储。")
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.create_user(db, user_in)
    return ok(data, msg="员工创建成功")

@router.put("/{id}", summary="修改员工资料", description="更新已有员工的资料，如果传入了 password 字段则一并重置密码。")
def update_user(
    user_in: UserUpdate,
    id: int = Path(..., description="要修改的员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.update_user(db, id, user_in)
    return ok(data, msg="资料修改成功")

@router.delete("/{id}", summary="注销员工账号", description="永久从数据库删除一位员工账户（无法恢复）。注意：初始 admin 管理员无法被删除。")
def delete_user(
    id: int = Path(..., description="要删除注销的员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    user_service.delete_user(db, id)
    return ok(None, msg="账号已永久注销")
