from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.response import ok
from schemas.customer import CustomerCreate, CustomerResponse
from services.customer_service import CustomerService
from core.permissions import get_current_user
from models.user import User

router = APIRouter(
    prefix="/customers",
    tags=["客户管理"]
)

@router.get("", summary="获取客户列表 (支持关键字搜索)")
def get_customers(
    search: str = Query(None, description="搜索公司名或联系人"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 读操作，无需审计日志
    service = CustomerService(db)
    customers = service.get_customer_list(search)
    return ok(data=customers)

@router.post("", summary="新建客户及关联联系人")
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 写操作，传入 user_id 以记录审计日志
    service = CustomerService(db)
    customer = service.create_customer(customer_in, current_user.id)
    return ok(data=customer)

@router.get("/{customer_id}", summary="获取客户详情及设备关联信息")
def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 读操作，无需审计日志
    service = CustomerService(db)
    customer = service.get_customer_detail(customer_id)
    return ok(data=customer)

