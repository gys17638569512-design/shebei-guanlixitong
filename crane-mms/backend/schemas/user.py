from pydantic import BaseModel, Field
from typing import Optional
from models.user import RoleEnum

class UserBase(BaseModel):
    username: str = Field(..., description="登录账号 (例如: tech01)")
    role: RoleEnum = Field(..., description="用户角色类别 (ADMIN, MANAGER, TECH)")
    name: str = Field(..., description="用户真实姓名 (例如: 张工)")
    phone: Optional[str] = Field(None, description="手机号，用于短信通知")
    manager_id: Optional[int] = Field(None, description="所属经理ID")
    display_name: Optional[str] = Field(None, description="显示名称")
    department: Optional[str] = Field(None, description="部门")
    job_title: Optional[str] = Field(None, description="岗位")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像地址")
    status: Optional[str] = Field("ACTIVE", description="账号状态")
    must_change_password: Optional[bool] = Field(False, description="是否强制改密")

class UserCreate(UserBase):
    password: str = Field(..., description="初始登录密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "tech001",
                "role": "TECH",
                "name": "张技术员",
                "password": "123"
            }
        }

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="登录账号 (可选更新)")
    role: Optional[RoleEnum] = Field(None, description="用户角色类别 (可选更新)")
    name: Optional[str] = Field(None, description="用户真实姓名 (可选更新)")
    phone: Optional[str] = Field(None, description="手机号 (可选更新)")
    manager_id: Optional[int] = Field(None, description="所属经理ID (可选更新)")
    password: Optional[str] = Field(None, description="新密码，如果传递则重置密码")
    display_name: Optional[str] = Field(None, description="显示名称")
    department: Optional[str] = Field(None, description="部门")
    job_title: Optional[str] = Field(None, description="岗位")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像地址")
    status: Optional[str] = Field(None, description="账号状态")
    must_change_password: Optional[bool] = Field(None, description="是否强制改密")


class UserPasswordReset(BaseModel):
    password: str = Field(..., description="重置后的密码")


class UserStatusUpdate(BaseModel):
    status: str = Field(..., description="ACTIVE/INACTIVE")


class UserSelfUpdate(BaseModel):
    name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="手机号")
    display_name: Optional[str] = Field(None, description="显示名称")
    email: Optional[str] = Field(None, description="邮箱")
    avatar_url: Optional[str] = Field(None, description="头像")
    password: Optional[str] = Field(None, description="新密码")

class UserResponse(UserBase):
    id: int = Field(..., description="用户系统唯一自增主键ID")
    mobile_bound: Optional[bool] = False
    wechat_bound: Optional[bool] = False
    last_login_at: Optional[str] = None
    password_updated_at: Optional[str] = None
    role_permissions: list[str] = Field(default_factory=list, description="角色默认权限")
    effective_permissions: list[str] = Field(default_factory=list, description="当前生效权限")
    user_overrides: dict = Field(default_factory=dict, description="用户个人权限覆盖")

    class Config:
        from_attributes = True
