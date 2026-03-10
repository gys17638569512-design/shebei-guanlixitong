from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from core.database import Base


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    contact_name = Column(String(50), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)

    # 客户门户登录字段
    login_phone = Column(String(20), nullable=True, index=True)
    sms_code = Column(String(6), nullable=True)
    sms_code_expires_at = Column(DateTime, nullable=True)
    
    # 关系
    equipments = relationship("Equipment", back_populates="customer")
    work_orders = relationship("WorkOrder", back_populates="customer")


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    position = Column(String(50))