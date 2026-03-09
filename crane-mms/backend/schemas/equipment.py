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

class EquipmentResponse(EquipmentBase):
    id: int
    parts: List[EquipmentPartResponse] = []

    class Config:
        from_attributes = True

class EquipmentUpdate(BaseModel):
    category: Optional[str] = None
    model_type: Optional[str] = None
    name: Optional[str] = None
    tonnage: Optional[str] = None
    span: Optional[str] = None
    lifting_height: Optional[str] = None
    work_class: Optional[str] = None
    installation_location: Optional[str] = None
    last_inspection_date: Optional[date] = None
    next_inspection_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    parts: Optional[List[EquipmentPartCreate]] = None
