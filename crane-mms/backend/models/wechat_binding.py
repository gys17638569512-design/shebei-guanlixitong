from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from core.database import Base


class WechatBinding(Base):
    __tablename__ = "wechat_bindings"

    id = Column(Integer, primary_key=True, index=True)
    owner_type = Column(String(30), nullable=False, index=True)
    owner_id = Column(Integer, nullable=False, index=True)
    scene = Column(String(30), nullable=False, index=True)
    openid = Column(String(100), nullable=False)
    unionid = Column(String(100), nullable=True)
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bound_mobile = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    bound_at = Column(DateTime, default=datetime.utcnow)
    unbound_at = Column(DateTime, nullable=True)
