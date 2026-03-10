from sqlalchemy import Column, Integer, String, Float, DateTime
from core.database import Base
from datetime import datetime

class Part(Base):
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True, index=True)
    part_no = Column(String(50), unique=True, index=True, nullable=False) # 零件编号
    name = Column(String(100), nullable=False) # 零件名称
    specification = Column(String(100))        # 规格型号
    unit = Column(String(20), default="件")    # 计量单位
    stock_quantity = Column(Integer, default=0, nullable=False) # 当前库存量
    warning_threshold = Column(Integer, default=5) # 预警库存
    price = Column(Float, default=0.0) # 预估单价
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
