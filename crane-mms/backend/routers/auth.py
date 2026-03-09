from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from core.database import get_db
from core.response import ok
from services.auth import login_user

router = APIRouter(prefix="/auth", tags=["认证模块"])


class LoginRequest(BaseModel):
    username: str = Field(..., description="登录账号 (例如: admin)")
    password: str = Field(..., description="登录密码 (例如: 123)")


@router.post("/login", summary="用户登录", description="接受明文账号密码，校验成功后返回带有排他性的 JWT Access Token 短令牌。")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    data = login_user(db, login_data.username, login_data.password)
    return ok(data)