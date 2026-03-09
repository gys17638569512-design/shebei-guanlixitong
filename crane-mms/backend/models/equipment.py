from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from core.database import Base


class Equipment(Base):
    __tablename__ = "equipments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    tonnage = Column(String(20), nullable=False)
    span = Column(String(20), nullable=False)
    lifting_height = Column(String(20), nullable=False)
    work_class = Column(String(20), nullable=False)
    installation_location = Column(Text, nullable=False)
    last_inspection_date = Column(Date)
    next_inspection_date = Column(Date)
    warranty_end_date = Column(Date)
    
    # 关系
    customer = relationship("Customer", back_populates="equipments")
    work_orders = relationship("WorkOrder", back_populates="equipment")
    parts = relationship("EquipmentPart", back_populates="equipment")


class EquipmentPart(Base):
    __tablename__ = "equipment_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False)
    part_name = Column(String(100), nullable=False)
    specification = Column(String(100))
    quantity = Column(Integer, default=1)
    
    # 关系
    equipment = relationship("Equipment", back_populates="parts")