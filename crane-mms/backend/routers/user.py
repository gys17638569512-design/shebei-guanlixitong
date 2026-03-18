from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.permissions import get_current_user, require_role
from core.response import ok
from models.user import User
from schemas.user import (
    UserCreate,
    UserPasswordReset,
    UserSelfUpdate,
    UserStatusUpdate,
    UserUpdate,
)
from schemas.wechat_binding import WechatBindingPayload
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
    data = user_service.get_users(db, skip=skip, limit=limit, role=role)
    return ok(data)


@router.get("/me", summary="获取当前员工自己的账号资料")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = user_service.get_current_user_profile(db, current_user)
    return ok(data)


@router.put("/me", summary="更新当前员工自己的账号资料")
def update_my_profile(
    payload: UserSelfUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = user_service.update_current_user_profile(db, current_user, payload)
    return ok(data, msg="个人资料已更新")


@router.post("/me/wechat-binding", summary="绑定当前员工微信")
def bind_my_wechat(
    payload: WechatBindingPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = user_service.bind_user_wechat(
        db,
        current_user,
        scene=payload.scene,
        openid=payload.openid,
        unionid=payload.unionid,
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
    )
    return ok(data, msg="微信绑定成功")


@router.delete("/me/wechat-binding", summary="解绑当前员工微信")
def unbind_my_wechat(
    scene: str = Query(..., description="绑定场景"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service.unbind_user_wechat(db, current_user, scene)
    return ok(None, msg="微信解绑成功")


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
    data = user_service.create_user(db, user_in, current_user.id)
    return ok(data, msg="员工创建成功")


@router.put("/{id}", summary="修改员工资料", description="更新已有员工的资料，如果传入了 password 字段则一并重置密码。")
def update_user(
    user_in: UserUpdate,
    id: int = Path(..., description="要修改的员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.update_user(db, id, user_in, current_user.id)
    return ok(data, msg="资料修改成功")


@router.put("/{id}/reset-password", summary="重置员工密码")
def reset_user_password(
    payload: UserPasswordReset,
    id: int = Path(..., description="员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.reset_user_password(db, id, payload.password, current_user.id)
    return ok(data, msg="密码已重置")


@router.put("/{id}/status", summary="启停员工账号")
def update_user_status(
    payload: UserStatusUpdate,
    id: int = Path(..., description="员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = user_service.update_user_status(db, id, payload.status, current_user.id)
    return ok(data, msg="账号状态已更新")


@router.delete("/{id}", summary="注销员工账号", description="永久从数据库删除一位员工账户（无法恢复）。注意：初始 admin 管理员无法被删除。")
def delete_user(
    id: int = Path(..., description="要删除注销的员工ID"),
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    user_service.delete_user(db, id)
    return ok(None, msg="账号已永久注销")
