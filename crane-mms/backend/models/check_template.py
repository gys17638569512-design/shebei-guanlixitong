from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime

class CheckTemplate(Base):
    __tablename__ = "check_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称，如：桥式起重机月检标准模板")
    category = Column(String(50), nullable=False, comment="适用设备大类")
    version = Column(Integer, nullable=False, default=1, comment="版本号，每次修改自动+1")
    items = Column(Text, nullable=False, comment="检查项JSON，格式：[{name, required, order}]")
    is_active = Column(Boolean, default=True, comment="是否为当前启用版本")
    created_by = Column(Integer, nullable=True, comment="创建人user_id")
    created_at = Column(DateTime, default=datetime.utcnow)
