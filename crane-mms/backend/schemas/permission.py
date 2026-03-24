from pydantic import BaseModel, Field


class RolePermissionUpdate(BaseModel):
    permissions: list[str] = Field(default_factory=list, description="角色默认权限列表")


class UserPermissionOverrideUpdate(BaseModel):
    allow_permissions: list[str] = Field(default_factory=list, description="显式授予的个人权限")
    deny_permissions: list[str] = Field(default_factory=list, description="显式禁用的个人权限")
