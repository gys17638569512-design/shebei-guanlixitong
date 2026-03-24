from typing import Any, List, Optional

from pydantic import BaseModel, Field


class EquipmentTemplateGroupCreate(BaseModel):
    category: str = Field(..., description="设备大类")
    model_type: str = Field(..., description="型式")
    name: str = Field(..., description="模板组名称")


class EquipmentTemplateVersionSave(BaseModel):
    group_id: int
    name: str
    manufacturer: Optional[str] = None
    tonnage_rule_type: str = Field(..., pattern="^(EXACT|RANGE)$")
    tonnage_exact: Optional[str] = None
    tonnage_min: Optional[float] = None
    tonnage_max: Optional[float] = None
    span_rule_type: str = Field(..., pattern="^(EXACT|RANGE)$")
    span_exact: Optional[str] = None
    span_min: Optional[float] = None
    span_max: Optional[float] = None
    default_params: dict[str, Any] = Field(default_factory=dict)
    parts: List[dict[str, Any]] = Field(default_factory=list)
    inspection_items: List[dict[str, Any]] = Field(default_factory=list)
    version_note: Optional[str] = None
    base_template_id: Optional[int] = None


class EquipmentTemplateCandidateCreate(BaseModel):
    equipment_id: int
    group_id: Optional[int] = None
    source_template_version_id: Optional[int] = None
    snapshot: dict[str, Any]
    diff_summary: List[dict[str, Any]] = Field(default_factory=list)


class CandidateReviewRequest(BaseModel):
    review_note: Optional[str] = None


class InspectionBaseTemplateSave(BaseModel):
    category: str
    model_type: str
    name: str
    tonnage_rule_type: str = Field(..., pattern="^(EXACT|RANGE)$")
    tonnage_exact: Optional[str] = None
    tonnage_min: Optional[float] = None
    tonnage_max: Optional[float] = None
    items: List[dict[str, Any]] = Field(default_factory=list)
    note: Optional[str] = None
