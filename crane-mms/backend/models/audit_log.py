from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    new_value = Column(Text, nullable=True)  # Store JSON as string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
