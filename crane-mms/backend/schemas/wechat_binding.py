from typing import Optional

from pydantic import BaseModel, Field


class WechatBindingPayload(BaseModel):
    scene: str = Field(..., description="绑定场景 ADMIN_WECHAT/CUSTOMER_WECHAT/WORKER_WECHAT")
    openid: str = Field(..., description="微信 OpenID")
    unionid: Optional[str] = Field(None, description="微信 UnionID")
    nickname: Optional[str] = Field(None, description="微信昵称")
    avatar_url: Optional[str] = Field(None, description="微信头像")


class WechatBindingResponse(BaseModel):
    scene: str
    owner_type: str
    owner_id: int
    openid: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bound_mobile: Optional[str] = None
    is_active: bool = False
    bound_at: Optional[str] = None
