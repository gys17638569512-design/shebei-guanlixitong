from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from core.database import Base


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    short_name = Column(String(50), nullable=True)
    system_name = Column(String(100), nullable=False)
    system_subtitle = Column(String(200), nullable=True)
    logo_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)
    seal_url = Column(String(500), nullable=True)
    support_phone = Column(String(30), nullable=True)
    support_email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    pc_login_title = Column(String(100), nullable=True)
    portal_login_title = Column(String(100), nullable=True)
    worker_login_title = Column(String(100), nullable=True)
    report_header_text = Column(String(200), nullable=True)
    report_footer_text = Column(String(200), nullable=True)
    theme_primary = Column(String(20), nullable=True)
    theme_secondary = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
