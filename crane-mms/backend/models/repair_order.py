from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, Boolean, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class RepairOrder(Base):
    __tablename__ = "repair_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False)
    tech_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 故障诊断
    fault_symptom = Column(Text, nullable=False, comment="现场故障现象描述")
    fault_component = Column(String(100), nullable=True, comment="故障定位(部件名称)")
    fault_cause = Column(String(50), nullable=True, comment="故障原因(自然老化/操作不当等)")
    site_photos = Column(JSON, nullable=True, comment="维修前中后带水印照片URL (JSON array)")
    
    # 配件与费用
    parts_used = Column(JSON, nullable=True, comment="更换零配件清单JSON")
    labor_fee = Column(DECIMAL(10, 2), default=0.0, comment="人工费")
    other_fee = Column(DECIMAL(10, 2), default=0.0, comment="其他费用")
    total_fee = Column(DECIMAL(10, 2), default=0.0, comment="总费用")
    is_warranty = Column(Boolean, default=False, comment="是否处于质保期内(免费)")
    
    # 结果与建议
    prevention_advice = Column(Text, nullable=True, comment="防范建议")
    client_sign_url = Column(String(500), nullable=True, comment="客户签名图片")
    fee_confirmed = Column(Boolean, default=False, comment="客户是否确认费用: 0-仅事实 1-确认费用")
    esign_cert_url = Column(String(500), nullable=True, comment="电子签章凭证")
    pdf_report_url = Column(String(500), nullable=True, comment="PDF报告单")
    
    # 状态
    status = Column(String(20), default="待处理", comment="状态：待处理/进行中/待客户确认/已完成")
    
    # 时间追踪
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="报修时间")
    completed_at = Column(TIMESTAMP, nullable=True, comment="完工时间")

    # 关联
    equipment = relationship("Equipment", backref="repair_orders")
    tech = relationship("User", foreign_keys=[tech_id])
