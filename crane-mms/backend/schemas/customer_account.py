from typing import Optional

from pydantic import BaseModel, Field


class CustomerAccountBase(BaseModel):
    customer_id: int = Field(..., description="所属客户公司 ID")
    parent_account_id: Optional[int] = Field(None, description="上级账号 ID")
    role: str = Field(..., description="账号角色 OWNER/ADMIN/SIGNER/VIEWER/REPORTER")
    username: str = Field(..., description="登录账号")
    name: str = Field(..., description="姓名")
    display_name: Optional[str] = Field(None, description="显示名称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像地址")
    is_owner: bool = Field(False, description="是否主账号")
    is_active: bool = Field(True, description="是否启用")


class CustomerAccountCreate(CustomerAccountBase):
    password: str = Field(..., description="初始密码")


class PortalSubAccountCreate(BaseModel):
    role: str = Field(..., description="账号角色")
    username: str = Field(..., description="登录账号")
    name: str = Field(..., description="姓名")
    display_name: Optional[str] = Field(None, description="显示名称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像地址")
    password: str = Field(..., description="初始密码")


class PortalSubAccountUpdate(BaseModel):
    role: Optional[str] = Field(None, description="账号角色")
    username: Optional[str] = Field(None, description="登录账号")
    name: Optional[str] = Field(None, description="姓名")
    display_name: Optional[str] = Field(None, description="显示名称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像地址")


class CustomerAccountStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="是否启用")


class CustomerAccountPasswordReset(BaseModel):
    password: str = Field(..., description="重置后的密码")


class CustomerAccountUpdate(BaseModel):
    parent_account_id: Optional[int] = None
    role: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    is_owner: Optional[bool] = None
    is_active: Optional[bool] = None
    must_change_password: Optional[bool] = None


class CustomerMainAccountUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class PortalCurrentAccountUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class PortalCurrentPasswordUpdate(BaseModel):
    password: str = Field(..., description="当前登录子账号的新密码")


class CustomerAccountResponse(CustomerAccountBase):
    id: int
    must_change_password: bool = False
    last_login_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    wechat_status: Optional[str] = None
    status_label: Optional[str] = None
    role_label: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerCompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    short_name: Optional[str] = None
    company_code: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    portal_mode: Optional[str] = None
    remark: Optional[str] = None


class CustomerCompanyProfileResponse(BaseModel):
    customer_id: int
    company_name: str
    short_name: Optional[str] = None
    company_code: Optional[str] = None
    logo_url: Optional[str] = None
    logo_text: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    portal_mode: Optional[str] = None
    remark: Optional[str] = None


class PortalAccountCenterResponse(BaseModel):
    mainAccount: dict
    subAccounts: list[dict]
    companyProfile: dict
