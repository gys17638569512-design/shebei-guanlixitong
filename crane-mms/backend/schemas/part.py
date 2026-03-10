from pydantic import BaseModel
from typing import Optional

class PartBase(BaseModel):
    part_no: str
    name: str
    specification: Optional[str] = None
    unit: str = "件"
    price: float = 0.0

class PartResponse(PartBase):
    id: int
    stock_quantity: int
    warning_threshold: int

    class Config:
        from_attributes = True

class PartCreate(PartBase):
    stock_quantity: int = 0
    warning_threshold: int = 5

class PartUpdate(BaseModel):
    name: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    warning_threshold: Optional[int] = None

class PartStockAdjust(BaseModel):
    action: str = "in" # in 或 out
    quantity: int
