from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum
from datetime import datetime


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"           # 待处理
    IN_PROGRESS = "IN_PROGRESS"   # 进行中
    PENDING_SIGN = "PENDING_SIGN" # 待签字
    COMPLETED = "COMPLETED"       # 已完成
    RESCHEDULED = "RESCHEDULED"   # 已改期
    REASSIGNED = "REASSIGNED"     # 已转派


class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_type = Column(String(20), nullable=False, default="月检")  # 周检/月检/季检/年检/临时维保
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_date = Column(Date, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    checkin_time = Column(DateTime)
    checkin_address = Column(Text)
    checkin_photo = Column(String(255))
    problem_description = Column(Text)
    solution = Column(Text)
    photo_urls = Column(Text)  # JSON 格式存储多个照片URL
    sign_url = Column(String(255))
    pdf_report_url = Column(String(255))
    esign_cert_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    customer = relationship("Customer", back_populates="work_orders", lazy="select")
    equipment = relationship("Equipment", back_populates="work_orders", lazy="select")
    technician = relationship("User", back_populates="work_orders", lazy="select")
    inspection_items = relationship("InspectionItem", back_populates="work_order", lazy="select")


class InspectionItem(Base):
    __tablename__ = "inspection_items"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    result = Column(String(20), nullable=False)  # NORMAL/ABNORMAL
    comment = Column(Text)
    photo_url = Column(String(255))
    
    # 关系
    work_order = relationship("WorkOrder", back_populates="inspection_items")