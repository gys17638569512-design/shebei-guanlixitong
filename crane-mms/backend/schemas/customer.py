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
    login_phone: Optional[str] = Field(None, description="客户门户登录手机号")

class CustomerCreate(CustomerBase):
    contacts: Optional[List[ContactCreate]] = Field(default=[], description="包含的其他附属联系人")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "宏达重工机器有限公司",
                "contact_name": "王经理",
                "contact_phone": "13800138000",
                "address": "上海市嘉定区工业路88号",
                "contacts": [
                    {
                        "name": "李技术员",
                        "phone": "13912345678",
                        "position": "设备负责人"
                    }
                ]
            }
        }

class CustomerResponse(CustomerBase):
    id: int
    contacts: List[ContactResponse] = []

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    company_name: Optional[str] = Field(None, description="客户公司名称")
    contact_name: Optional[str] = Field(None, description="主联系人姓名")
    contact_phone: Optional[str] = Field(None, description="主联系人电话")
    address: Optional[str] = Field(None, description="客户公司地址")
    login_phone: Optional[str] = Field(None, description="客户门户登录手机号")
    contacts: Optional[List[ContactCreate]] = Field(None, description="包含的其他附属联系人(如果传，则覆盖原有列表)")
