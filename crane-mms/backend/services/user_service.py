from datetime import datetime

from sqlalchemy.orm import Session

from core.audit import write_audit_log
from core.exceptions import BusinessError, NotFoundError
from core.security import get_password_hash
from models.employee_profile import EmployeeProfile
from models.wechat_binding import WechatBinding
from repositories import user as user_repo
from schemas.user import UserCreate, UserSelfUpdate, UserUpdate


PROFILE_FIELDS = {"display_name", "department", "job_title", "email", "avatar_url", "status", "must_change_password"}
BASE_FIELDS = {"username", "role", "name", "phone", "manager_id"}


def _get_profile(db: Session, user_id: int, create: bool = False) -> EmployeeProfile | None:
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id).first()
    if profile or not create:
        return profile

    profile = EmployeeProfile(user_id=user_id, status="ACTIVE", mobile_bound=False)
    db.add(profile)
    db.flush()
    return profile


def _build_wechat_bound_map(db: Session, user_ids: list[int]) -> set[int]:
    if not user_ids:
        return set()

    bindings = db.query(WechatBinding).filter(
        WechatBinding.owner_type == "USER",
        WechatBinding.owner_id.in_(user_ids),
        WechatBinding.is_active == True,
    ).all()
    return {binding.owner_id for binding in bindings}


def _serialize_user(user, profile: EmployeeProfile | None = None, wechat_bound: bool = False) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "name": user.name,
        "phone": user.phone,
        "manager_id": user.manager_id,
        "display_name": profile.display_name if profile and profile.display_name else user.name,
        "department": profile.department if profile else None,
        "job_title": profile.job_title if profile else None,
        "email": profile.email if profile else None,
        "avatar_url": profile.avatar_url if profile else None,
        "status": profile.status if profile else "ACTIVE",
        "must_change_password": profile.must_change_password if profile else False,
        "mobile_bound": bool((profile.mobile_bound if profile else False) or user.phone),
        "wechat_bound": wechat_bound,
        "last_login_at": profile.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if profile and profile.last_login_at else None,
        "password_updated_at": profile.password_updated_at.strftime("%Y-%m-%d %H:%M:%S") if profile and profile.password_updated_at else None,
    }


def get_users(db: Session, skip: int = 0, limit: int = 100, role: str | None = None):
    total, items = user_repo.get_users(db, skip=0, limit=100000 if role else limit)
    if role:
        items = [
            item for item in items
            if str(getattr(item.role, "value", item.role)) == role or str(item.role) == role
        ]
        total = len(items)
        items = items[skip: skip + limit]

    user_ids = [item.id for item in items]
    profiles = db.query(EmployeeProfile).filter(EmployeeProfile.user_id.in_(user_ids)).all() if user_ids else []
    profile_map = {profile.user_id: profile for profile in profiles}
    bound_set = _build_wechat_bound_map(db, user_ids)

    return {
        "total": total,
        "items": [_serialize_user(item, profile_map.get(item.id), item.id in bound_set) for item in items],
    }


def get_user(db: Session, user_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("用户未找到")

    profile = _get_profile(db, user_id, create=False)
    bound_set = _build_wechat_bound_map(db, [user_id])
    return _serialize_user(user, profile, user_id in bound_set)


def create_user(db: Session, user_in: UserCreate, operator_id: int):
    if user_repo.get_user_by_username(db, user_in.username):
        raise BusinessError("该用户名已存在，请更换重试")

    payload = user_in.model_dump()
    profile_data = {key: payload.pop(key, None) for key in PROFILE_FIELDS}
    password = payload.pop("password")
    payload["password_hash"] = get_password_hash(password)

    user = user_repo.create_user(db, payload)
    profile = EmployeeProfile(
        user_id=user.id,
        display_name=profile_data.get("display_name"),
        department=profile_data.get("department"),
        job_title=profile_data.get("job_title"),
        email=profile_data.get("email"),
        avatar_url=profile_data.get("avatar_url"),
        status=profile_data.get("status") or "ACTIVE",
        must_change_password=profile_data.get("must_change_password", True),
        mobile_bound=bool(user.phone),
        password_updated_at=datetime.utcnow(),
    )
    db.add(profile)
    db.flush()

    write_audit_log(
        db=db,
        user_id=operator_id,
        action="CREATE",
        table_name="users",
        record_id=user.id,
        new_value={"username": user.username, "role": getattr(user.role, "value", user.role), "status": profile.status},
    )
    db.commit()
    return _serialize_user(user, profile, False)


def update_user(db: Session, user_id: int, user_in: UserUpdate, operator_id: int):
    db_user = user_repo.get_user_by_id(db, user_id)
    if not db_user:
        raise NotFoundError("用户未找到")

    update_data = user_in.model_dump(exclude_unset=True)
    profile = _get_profile(db, user_id, create=True)

    if "username" in update_data and update_data["username"] != db_user.username:
        if user_repo.get_user_by_username(db, update_data["username"]):
            raise BusinessError("更新失败：该用户名已被其他账户使用")

    base_updates = {key: value for key, value in update_data.items() if key in BASE_FIELDS}
    profile_updates = {key: value for key, value in update_data.items() if key in PROFILE_FIELDS}

    if "password" in update_data:
        base_updates["password_hash"] = get_password_hash(update_data["password"])
        profile.password_updated_at = datetime.utcnow()

    user = user_repo.update_user(db, db_user, base_updates)
    for key, value in profile_updates.items():
        setattr(profile, key, value)
    profile.mobile_bound = bool(user.phone)

    db.flush()
    write_audit_log(
        db=db,
        user_id=operator_id,
        action="UPDATE",
        table_name="users",
        record_id=user.id,
        new_value={**base_updates, **profile_updates, "mobile_bound": profile.mobile_bound},
    )
    db.commit()
    return _serialize_user(user, profile, user_id in _build_wechat_bound_map(db, [user_id]))


def reset_user_password(db: Session, user_id: int, password: str, operator_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("用户未找到")

    profile = _get_profile(db, user_id, create=True)
    user.password_hash = get_password_hash(password)
    profile.must_change_password = True
    profile.password_updated_at = datetime.utcnow()
    db.flush()

    write_audit_log(
        db=db,
        user_id=operator_id,
        action="UPDATE",
        table_name="users",
        record_id=user.id,
        new_value={"password_reset": True, "must_change_password": True},
    )
    db.commit()
    return _serialize_user(user, profile, user_id in _build_wechat_bound_map(db, [user_id]))


def update_user_status(db: Session, user_id: int, status: str, operator_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("用户未找到")

    profile = _get_profile(db, user_id, create=True)
    profile.status = status
    db.flush()

    write_audit_log(
        db=db,
        user_id=operator_id,
        action="UPDATE",
        table_name="users",
        record_id=user.id,
        new_value={"status": status},
    )
    db.commit()
    return _serialize_user(user, profile, user_id in _build_wechat_bound_map(db, [user_id]))


def get_current_user_profile(db: Session, current_user):
    profile = _get_profile(db, current_user.id, create=True)
    bound_set = _build_wechat_bound_map(db, [current_user.id])
    return _serialize_user(current_user, profile, current_user.id in bound_set)


def update_current_user_profile(db: Session, current_user, payload: UserSelfUpdate):
    profile = _get_profile(db, current_user.id, create=True)
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        current_user.name = update_data["name"]
    if "phone" in update_data:
        current_user.phone = update_data["phone"]
        profile.mobile_bound = bool(update_data["phone"])
    if "display_name" in update_data:
        profile.display_name = update_data["display_name"]
    if "email" in update_data:
        profile.email = update_data["email"]
    if "avatar_url" in update_data:
        profile.avatar_url = update_data["avatar_url"]
    if "password" in update_data:
        current_user.password_hash = get_password_hash(update_data["password"])
        profile.password_updated_at = datetime.utcnow()

    db.flush()
    write_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        table_name="users",
        record_id=current_user.id,
        new_value={"self_update": True, **{key: value for key, value in update_data.items() if key != "password"}},
    )
    db.commit()
    return _serialize_user(current_user, profile, current_user.id in _build_wechat_bound_map(db, [current_user.id]))


def bind_user_wechat(db: Session, current_user, scene: str, openid: str, unionid: str | None = None, nickname: str | None = None, avatar_url: str | None = None):
    binding = db.query(WechatBinding).filter(
        WechatBinding.owner_type == "USER",
        WechatBinding.owner_id == current_user.id,
        WechatBinding.scene == scene,
    ).first()

    if binding:
        binding.openid = openid
        binding.unionid = unionid
        binding.nickname = nickname
        binding.avatar_url = avatar_url
        binding.bound_mobile = current_user.phone
        binding.is_active = True
        binding.unbound_at = None
    else:
        binding = WechatBinding(
            owner_type="USER",
            owner_id=current_user.id,
            scene=scene,
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url,
            bound_mobile=current_user.phone,
            is_active=True,
        )
        db.add(binding)
        db.flush()

    write_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        table_name="wechat_bindings",
        record_id=binding.id,
        new_value={"scene": scene, "openid": openid, "owner_type": "USER"},
    )
    db.commit()
    return {
        "scene": binding.scene,
        "owner_type": binding.owner_type,
        "owner_id": binding.owner_id,
        "openid": binding.openid,
        "nickname": binding.nickname,
        "avatar_url": binding.avatar_url,
        "bound_mobile": binding.bound_mobile,
        "is_active": binding.is_active,
        "bound_at": binding.bound_at.strftime("%Y-%m-%d %H:%M:%S") if binding.bound_at else None,
    }


def unbind_user_wechat(db: Session, current_user, scene: str):
    binding = db.query(WechatBinding).filter(
        WechatBinding.owner_type == "USER",
        WechatBinding.owner_id == current_user.id,
        WechatBinding.scene == scene,
        WechatBinding.is_active == True,
    ).first()
    if not binding:
        raise NotFoundError("微信绑定记录不存在")

    binding.is_active = False
    binding.unbound_at = datetime.utcnow()
    db.flush()
    write_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        table_name="wechat_bindings",
        record_id=binding.id,
        new_value={"scene": scene, "is_active": False},
    )
    db.commit()
    return True


def delete_user(db: Session, user_id: int):
    if user_id == 1:
        raise BusinessError("系统的初始超级管理员账户不允许被删除")

    db_user = user_repo.get_user_by_id(db, user_id)
    if not db_user:
        raise NotFoundError("用户未找到")

    user_repo.delete_user(db, db_user)
    db.commit()
    return True
