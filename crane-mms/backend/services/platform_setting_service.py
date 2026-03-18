from datetime import datetime

from sqlalchemy.orm import Session

from core.audit import write_audit_log
from models.platform_setting import PlatformSetting
from schemas.platform_setting import PlatformSettingUpdate


DEFAULT_PLATFORM_SETTING = {
    "company_name": "数字化起重机维修维保系统",
    "short_name": "起重机维保",
    "system_name": "数字化起重机维修维保系统",
    "system_subtitle": "全生命周期设备服务平台",
    "logo_url": "/brand-mark.svg",
    "favicon_url": "/brand-mark.svg",
    "seal_url": "/brand-mark.svg",
    "support_phone": "400-800-1234",
    "support_email": "service@example.com",
    "address": "中国 · 设备运维服务中心",
    "pc_login_title": "管理端登录",
    "portal_login_title": "客户端登录",
    "worker_login_title": "工人端登录",
    "report_header_text": "数字化起重机维修维保系统",
    "report_footer_text": "如有疑问请联系平台客服",
    "theme_primary": "#1677ff",
    "theme_secondary": "#0ea5e9",
    "is_active": True,
}


def _serialize_setting(setting: PlatformSetting) -> dict:
    logo_url = "/brand-mark.svg" if setting.logo_url == "/static/brand-mark.svg" else setting.logo_url
    favicon_url = "/brand-mark.svg" if setting.favicon_url == "/static/brand-mark.svg" else setting.favicon_url
    seal_url = "/brand-mark.svg" if setting.seal_url == "/static/brand-mark.svg" else setting.seal_url
    return {
        "id": setting.id,
        "company_name": setting.company_name,
        "short_name": setting.short_name,
        "system_name": setting.system_name,
        "system_subtitle": setting.system_subtitle,
        "logo_url": logo_url,
        "favicon_url": favicon_url,
        "seal_url": seal_url,
        "support_phone": setting.support_phone,
        "support_email": setting.support_email,
        "address": setting.address,
        "pc_login_title": setting.pc_login_title,
        "portal_login_title": setting.portal_login_title,
        "worker_login_title": setting.worker_login_title,
        "report_header_text": setting.report_header_text,
        "report_footer_text": setting.report_footer_text,
        "theme_primary": setting.theme_primary,
        "theme_secondary": setting.theme_secondary,
        "is_active": setting.is_active,
        "created_at": setting.created_at.strftime("%Y-%m-%d %H:%M:%S") if setting.created_at else None,
        "updated_at": setting.updated_at.strftime("%Y-%m-%d %H:%M:%S") if setting.updated_at else None,
    }


def get_or_create_platform_setting(db: Session) -> PlatformSetting:
    setting = db.query(PlatformSetting).filter(PlatformSetting.is_active == True).order_by(PlatformSetting.id.desc()).first()
    if setting:
        return setting

    setting = PlatformSetting(**DEFAULT_PLATFORM_SETTING)
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def get_platform_setting(db: Session) -> dict:
    setting = get_or_create_platform_setting(db)
    return _serialize_setting(setting)


def update_platform_setting(db: Session, payload: PlatformSettingUpdate, operator_id: int) -> dict:
    setting = get_or_create_platform_setting(db)
    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(setting, key, value)

    setting.updated_at = datetime.utcnow()
    db.flush()
    write_audit_log(
        db=db,
        user_id=operator_id,
        action="UPDATE",
        table_name="platform_settings",
        record_id=setting.id,
        new_value={**_serialize_setting(setting), **update_data},
    )
    db.commit()
    db.refresh(setting)
    return _serialize_setting(setting)
