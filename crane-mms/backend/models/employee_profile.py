from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    display_name = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    must_change_password = Column(Boolean, nullable=False, default=False)
    mobile_bound = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime, nullable=True)
    password_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
