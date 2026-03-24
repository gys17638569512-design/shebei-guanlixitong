from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from core.database import Base
from models.user import RoleEnum


class RolePermissionProfile(Base):
    __tablename__ = "role_permission_profiles"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(RoleEnum), unique=True, nullable=False, index=True)
    permissions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserPermissionOverride(Base):
    __tablename__ = "user_permission_overrides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    allow_permissions_json = Column(Text, nullable=False, default="[]")
    deny_permissions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
