from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.user import User
from schemas.platform_setting import PlatformSettingUpdate
from services import platform_setting_service


router = APIRouter(prefix="/settings", tags=["平台配置"])


@router.get("/platform", summary="获取当前平台品牌配置")
def get_platform_setting(
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = platform_setting_service.get_platform_setting(db)
    return ok(data)


@router.put("/platform", summary="更新平台品牌配置")
def update_platform_setting(
    payload: PlatformSettingUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    data = platform_setting_service.update_platform_setting(db, payload, current_user.id)
    return ok(data, msg="平台品牌配置已更新")
