from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any, Dict
from datetime import datetime

class RepairOrderBase(BaseModel):
    equipment_id: int
    fault_symptom: str
    fault_component: Optional[str] = None
    fault_cause: Optional[str] = None

class RepairOrderCreate(RepairOrderBase):
    tech_id: Optional[int] = None

class RepairOrderUpdate(BaseModel):
    fault_symptom: Optional[str] = None
    fault_component: Optional[str] = None
    fault_cause: Optional[str] = None
    site_photos: Optional[List[str]] = None
    parts_used: Optional[List[Dict[str, Any]]] = None
    labor_fee: Optional[float] = None
    other_fee: Optional[float] = None
    total_fee: Optional[float] = None
    is_warranty: Optional[bool] = None
    prevention_advice: Optional[str] = None
    client_sign_url: Optional[str] = None
    fee_confirmed: Optional[bool] = None
    status: Optional[str] = None

class RepairOrderResponse(RepairOrderBase):
    id: int
    tech_id: Optional[int]
    site_photos: Optional[List[str]]
    parts_used: Optional[List[Dict[str, Any]]]
    labor_fee: float
    other_fee: float
    total_fee: float
    is_warranty: bool
    prevention_advice: Optional[str]
    client_sign_url: Optional[str]
    fee_confirmed: bool
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
