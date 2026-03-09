from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
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
    
    class Config:
        env_file = ".env"


settings = Settings()