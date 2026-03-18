from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时，满足现场长时间作业需求
    
    # 腾讯云COS配置
    COS_SECRET_ID: Optional[str] = None
    COS_SECRET_KEY: Optional[str] = None
    COS_BUCKET: Optional[str] = None
    COS_REGION: str = "ap-beijing"
    
    # e签宝配置
    ESIGN_MOCK: bool = True
    ESIGN_APP_ID: Optional[str] = None
    ESIGN_APP_SECRET: Optional[str] = None
    
    # 其他配置
    DEBUG: bool = True

    # 阶段二：短信配置
    SMS_PROVIDER: str = "aliyun"
    SMS_ACCESS_KEY_ID: Optional[str] = None
    SMS_ACCESS_KEY_SECRET: Optional[str] = None
    SMS_SIGN_NAME: str = "数字化起重机维修维保系统"
    SMS_TEMPLATE_CODE_DISPATCH: Optional[str] = None
    SMS_TEMPLATE_CODE_SIGN: Optional[str] = None
    SMS_TEMPLATE_CODE_REPORT: Optional[str] = None
    SMS_TEMPLATE_CODE_VERIFY: Optional[str] = None
    SMS_MOCK: bool = True  # True 时仅打印日志，不真实发送

    # 阶段二：微信配置
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_TOKEN: Optional[str] = None
    WECHAT_ENCODING_KEY: Optional[str] = None
    WECHAT_MOCK: bool = True

    # 阶段二：客户门户
    CUSTOMER_PORTAL_URL: str = "http://localhost:3001"
    CUSTOMER_JWT_SECRET: str = "customer_portal_secret_key_2024"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
