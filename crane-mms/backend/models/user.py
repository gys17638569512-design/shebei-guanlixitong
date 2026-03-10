from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    TECH = "TECH"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True, comment="手机号，用于短信通知")
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属经理ID，TECH角色必填")
    
    # 关系
    work_orders = relationship("WorkOrder", back_populates="technician")