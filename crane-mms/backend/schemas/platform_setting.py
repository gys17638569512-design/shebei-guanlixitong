from pydantic import BaseModel, Field
from typing import Optional


class PlatformSettingBase(BaseModel):
    company_name: str = Field(..., description="平台公司全称")
    short_name: Optional[str] = Field(None, description="平台简称")
    system_name: str = Field(..., description="系统显示名称")
    system_subtitle: Optional[str] = Field(None, description="系统副标题")
    logo_url: Optional[str] = Field(None, description="Logo 地址")
    favicon_url: Optional[str] = Field(None, description="浏览器图标地址")
    seal_url: Optional[str] = Field(None, description="印章地址")
    support_phone: Optional[str] = Field(None, description="客服电话")
    support_email: Optional[str] = Field(None, description="客服邮箱")
    address: Optional[str] = Field(None, description="联系地址")
    pc_login_title: Optional[str] = Field(None, description="管理端登录标题")
    portal_login_title: Optional[str] = Field(None, description="客户端登录标题")
    worker_login_title: Optional[str] = Field(None, description="工人端登录标题")
    report_header_text: Optional[str] = Field(None, description="报告页头文案")
    report_footer_text: Optional[str] = Field(None, description="报告页脚文案")
    theme_primary: Optional[str] = Field(None, description="主色")
    theme_secondary: Optional[str] = Field(None, description="辅色")
    is_active: bool = Field(True, description="是否启用")


class PlatformSettingUpdate(BaseModel):
    company_name: Optional[str] = None
    short_name: Optional[str] = None
    system_name: Optional[str] = None
    system_subtitle: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    seal_url: Optional[str] = None
    support_phone: Optional[str] = None
    support_email: Optional[str] = None
    address: Optional[str] = None
    pc_login_title: Optional[str] = None
    portal_login_title: Optional[str] = None
    worker_login_title: Optional[str] = None
    report_header_text: Optional[str] = None
    report_footer_text: Optional[str] = None
    theme_primary: Optional[str] = None
    theme_secondary: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformSettingResponse(PlatformSettingBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
