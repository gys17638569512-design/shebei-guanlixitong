from pydantic import BaseModel, Field
from typing import Optional
from models.user import RoleEnum

class UserBase(BaseModel):
    username: str = Field(..., description="登录账号 (例如: tech01)")
    role: RoleEnum = Field(..., description="用户角色类别 (ADMIN, MANAGER, TECH)")
    name: str = Field(..., description="用户真实姓名 (例如: 张工)")
    phone: Optional[str] = Field(None, description="手机号，用于短信通知")
    manager_id: Optional[int] = Field(None, description="所属经理ID")

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

class UserResponse(UserBase):
    id: int = Field(..., description="用户系统唯一自增主键ID")

    class Config:
        from_attributes = True
