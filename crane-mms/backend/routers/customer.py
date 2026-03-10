from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.response import ok
from schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from services.customer_service import CustomerService
from core.permissions import get_current_user, require_role
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
    customers = service.get_customer_list(search, current_user)
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

@router.put("/{customer_id}", summary="修改客户资料")
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"]))
):
    service = CustomerService(db)
    customer = service.update_customer(customer_id, customer_in, current_user.id)
    return ok(data=customer, msg="客户信息已更新")

@router.delete("/{customer_id}", summary="删除客户")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    service = CustomerService(db)
    service.delete_customer(customer_id, current_user.id)
    return ok(None, msg="客户已删除")
