from pydantic import BaseModel, Field
from typing import List, Optional

class ContactBase(BaseModel):
    name: str = Field(..., description="联系人姓名")
    phone: str = Field(..., description="联系人电话")
    position: Optional[str] = Field("其它联系人", description="联系人职位/角色")

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    customer_id: int

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    company_name: str = Field(..., description="客户公司名称")
    contact_name: str = Field(..., description="主联系人姓名")
    contact_phone: str = Field(..., description="主联系人电话")
    address: str = Field(..., description="客户公司地址")

class CustomerCreate(CustomerBase):
    contacts: Optional[List[ContactCreate]] = Field(default=[], description="包含的其他附属联系人")

class CustomerResponse(CustomerBase):
    id: int
    contacts: List[ContactResponse] = []

    class Config:
        from_attributes = True
