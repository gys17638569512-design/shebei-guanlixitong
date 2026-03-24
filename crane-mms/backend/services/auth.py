from datetime import datetime

from sqlalchemy.orm import Session

from core.exceptions import UnauthorizedError
from core.security import create_access_token, verify_password
from models.employee_profile import EmployeeProfile
from models.wechat_binding import WechatBinding
from repositories import user as user_repo
from services.permission_service import PermissionService

def login_user(db: Session, username: str, password: str) -> dict:
    usr = user_repo.get_user_by_username(db, username)
    if not usr or not verify_password(password, usr.password_hash):
        raise UnauthorizedError("Incorrect username or password")

    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == usr.id).first()
    if not profile:
        profile = EmployeeProfile(user_id=usr.id, status="ACTIVE", mobile_bound=bool(usr.phone))
        db.add(profile)
        db.flush()

    profile.last_login_at = datetime.utcnow()
    profile.mobile_bound = bool(usr.phone)
    db.commit()

    wechat_bound = db.query(WechatBinding).filter(
        WechatBinding.owner_type == "USER",
        WechatBinding.owner_id == usr.id,
        WechatBinding.is_active == True,
    ).first() is not None

    permission_bundle = PermissionService(db).get_user_permission_bundle(usr)
    
    access_token = create_access_token(data={"sub": usr.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": usr.id,
            "username": usr.username,
            "name": usr.name,
            "role": usr.role,
            "phone": usr.phone,
            "display_name": profile.display_name or usr.name,
            "department": profile.department,
            "job_title": profile.job_title,
            "status": profile.status,
            "mobile_bound": profile.mobile_bound,
            "wechat_bound": wechat_bound,
            "role_permissions": permission_bundle["role_permissions"],
            "user_overrides": permission_bundle["user_overrides"],
            "effective_permissions": permission_bundle["effective_permissions"],
        }
    }
