from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class EquipmentPartBase(BaseModel):
    part_name: str = Field(..., description="部件名称")
    specification: Optional[str] = Field(None, description="规格参数")
    quantity: int = Field(1, description="数量")

class EquipmentPartCreate(EquipmentPartBase):
    pass

class EquipmentPartResponse(EquipmentPartBase):
    id: int
    equipment_id: int

    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    customer_id: int = Field(..., description="所属客户ID")
    category: str = Field(..., description="设备大类(如桥式起重机)")
    model_type: str = Field(..., description="型式(如QD型)")
    name: str = Field(..., description="设备名称")
    manufacturer: Optional[str] = Field(None, description="设备厂家")
    tonnage: str = Field(..., description="吨位")
    span: str = Field(..., description="跨度")
    lifting_height: str = Field(..., description="起升高度")
    work_class: str = Field(..., description="工作级别")
    installation_location: str = Field(..., description="安装位置")
    last_inspection_date: Optional[date] = Field(None, description="上次特检日期")
    next_inspection_date: Optional[date] = Field(None, description="下次特检日期")
    warranty_end_date: Optional[date] = Field(None, description="质保到期日")

class EquipmentCreate(EquipmentBase):
    parts: Optional[List[EquipmentPartCreate]] = Field(default=[], description="部件清单")
    inspection_items: Optional[List[dict]] = Field(default=[], description="建议检修项")
    applied_template_id: Optional[int] = Field(None, description="已应用模板组ID")
    applied_template_version: Optional[int] = Field(None, description="已应用模板版本号")
    submit_as_template_candidate: bool = Field(False, description="是否提交为模板候选")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "category": "桥式起重机",
                "model_type": "QD型",
                "name": "成品库1号行车",
                "manufacturer": "沪工",
                "tonnage": "10t",
                "span": "22.5m",
                "lifting_height": "9m",
                "work_class": "A5",
                "installation_location": "成品车间A区",
                "last_inspection_date": "2023-12-01",
                "next_inspection_date": "2024-12-01",
                "warranty_end_date": "2025-06-01",
                "inspection_items": [
                    {"item_name": "钢丝绳检查", "description": "检查磨损情况", "required": True}
                ],
                "applied_template_id": 1,
                "applied_template_version": 2,
                "submit_as_template_candidate": True,
                "parts": [
                    {"part_name": "主起升机构", "specification": "10t专用", "quantity": 1},
                    {"part_name": "大车运行电机", "specification": "3.0kW", "quantity": 4}
                ]
            }
        }

class EquipmentResponse(EquipmentBase):
    id: int
    parts: List[EquipmentPartResponse] = []
    inspection_items: List[dict] = []
    applied_template_id: Optional[int] = None
    applied_template_version: Optional[int] = None
    submit_as_template_candidate: bool = False

    class Config:
        from_attributes = True

class EquipmentUpdate(BaseModel):
    category: Optional[str] = None
    model_type: Optional[str] = None
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    tonnage: Optional[str] = None
    span: Optional[str] = None
    lifting_height: Optional[str] = None
    work_class: Optional[str] = None
    installation_location: Optional[str] = None
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    parts: Optional[List[EquipmentPartCreate]] = None
    inspection_items: Optional[List[dict]] = None
    applied_template_id: Optional[int] = None
    applied_template_version: Optional[int] = None
    submit_as_template_candidate: Optional[bool] = None
