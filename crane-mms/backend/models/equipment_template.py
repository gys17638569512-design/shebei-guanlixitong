from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class EquipmentTemplateGroup(Base):
    __tablename__ = "equipment_template_groups"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    versions = relationship(
        "EquipmentTemplateVersion",
        back_populates="group",
        cascade="all, delete-orphan",
        foreign_keys="EquipmentTemplateVersion.group_id",
    )


class EquipmentTemplateVersion(Base):
    __tablename__ = "equipment_template_versions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("equipment_template_groups.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    name = Column(String(120), nullable=False)
    manufacturer = Column(String(100), nullable=True, index=True)
    tonnage_rule_type = Column(String(20), nullable=False, default="EXACT")
    tonnage_exact = Column(String(50), nullable=True)
    tonnage_min = Column(Float, nullable=True)
    tonnage_max = Column(Float, nullable=True)
    span_rule_type = Column(String(20), nullable=False, default="EXACT")
    span_exact = Column(String(50), nullable=True)
    span_min = Column(Float, nullable=True)
    span_max = Column(Float, nullable=True)
    default_params_json = Column(Text, nullable=False, default="{}")
    parts_json = Column(Text, nullable=False, default="[]")
    inspection_items_json = Column(Text, nullable=False, default="[]")
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    version_note = Column(Text, nullable=True)
    base_template_id = Column(Integer, ForeignKey("inspection_base_templates.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    group = relationship("EquipmentTemplateGroup", back_populates="versions", foreign_keys=[group_id])
    base_template = relationship("InspectionBaseTemplate", back_populates="template_versions")


class InspectionBaseTemplate(Base):
    __tablename__ = "inspection_base_templates"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    tonnage_rule_type = Column(String(20), nullable=False, default="EXACT")
    tonnage_exact = Column(String(50), nullable=True)
    tonnage_min = Column(Float, nullable=True)
    tonnage_max = Column(Float, nullable=True)
    items_json = Column(Text, nullable=False, default="[]")
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    note = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    template_versions = relationship("EquipmentTemplateVersion", back_populates="base_template")


class EquipmentTemplateCandidate(Base):
    __tablename__ = "equipment_template_candidates"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("equipment_template_groups.id"), nullable=True, index=True)
    source_template_version_id = Column(Integer, ForeignKey("equipment_template_versions.id"), nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), nullable=False, default="PENDING_REVIEW", index=True)
    snapshot_json = Column(Text, nullable=False)
    diff_summary_json = Column(Text, nullable=False, default="[]")
    review_note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    equipment = relationship("Equipment", foreign_keys=[equipment_id])
    group = relationship("EquipmentTemplateGroup", foreign_keys=[group_id])
    source_template_version = relationship("EquipmentTemplateVersion", foreign_keys=[source_template_version_id])
