from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.user import User
from schemas.customer_account import (
    CustomerAccountCreate,
    CustomerAccountUpdate,
    CustomerCompanyProfileUpdate,
)
from services import customer_account_service


router = APIRouter(prefix="/customer-accounts", tags=["客户账号中心"])


@router.get("", summary="获取指定客户公司的账号列表")
def get_customer_accounts(
    customer_id: int = Query(..., description="客户公司 ID"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = customer_account_service.list_customer_accounts(db, customer_id)
    return ok(data)


@router.post("", summary="为客户公司创建主账号或子账号")
def create_customer_account(
    payload: CustomerAccountCreate,
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = customer_account_service.create_customer_account(db, payload, current_user.id)
    return ok(data, msg="客户账号创建成功")


@router.put("/{account_id}", summary="更新客户账号")
def update_customer_account(
    payload: CustomerAccountUpdate,
    account_id: int = Path(..., description="客户账号 ID"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_customer_account(db, account_id, payload, current_user.id)
    return ok(data, msg="客户账号已更新")


@router.get("/customer/{customer_id}/company-profile", summary="获取客户公司资料扩展信息")
def get_customer_company_profile(
    customer_id: int = Path(..., description="客户公司 ID"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = customer_account_service.get_customer_company_profile(db, customer_id)
    return ok(data)


@router.put("/customer/{customer_id}/company-profile", summary="更新客户公司资料扩展信息")
def update_customer_company_profile(
    payload: CustomerCompanyProfileUpdate,
    customer_id: int = Path(..., description="客户公司 ID"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_customer_company_profile(db, customer_id, payload, current_user.id)
    return ok(data, msg="客户公司资料已更新")
