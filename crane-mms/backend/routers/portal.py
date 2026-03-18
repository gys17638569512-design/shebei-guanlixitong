"""
客户门户认证路由
---
POST /api/v1/portal/auth/send_code  - 发送短信验证码
POST /api/v1/portal/auth/login      - 验证码登录，返回客户 JWT
GET  /api/v1/portal/me              - 获取当前客户单位资料
GET  /api/v1/portal/equipments      - 获取客户设备一览表
GET  /api/v1/portal/orders          - 客户查看自己的维保/维修记录
GET  /api/v1/portal/orders/{id}     - 查看详细记录
POST /api/v1/portal/orders/{id}/sign - 提交客户签字确认
"""
import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, BackgroundTasks
from sqlalchemy.orm import Session
from jose import jwt

from core.database import get_db
from core.response import ok
from core.security import verify_password
from core.settings import settings
from core.sms import send_verify_code_sms
from models.customer_account import CustomerAccount
from models.customer import Customer
from models.work_order import WorkOrder, OrderStatus
from schemas.customer_account import (
    CustomerAccountPasswordReset,
    CustomerAccountStatusUpdate,
    CustomerCompanyProfileUpdate,
    CustomerMainAccountUpdate,
    PortalCurrentAccountUpdate,
    PortalCurrentPasswordUpdate,
    PortalSubAccountCreate,
    PortalSubAccountUpdate,
)
from schemas.wechat_binding import WechatBindingPayload
from services import customer_account_service

router = APIRouter(prefix="/portal", tags=["客户门户"])


def _generate_customer_token(customer_id: int, account_id: int | None = None, account_type: str = "CUSTOMER") -> str:
    payload = {
        "sub": str(customer_id),
        "type": "customer",
        "account_id": account_id,
        "account_type": account_type,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.CUSTOMER_JWT_SECRET, algorithm="HS256")


def _verify_customer_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.CUSTOMER_JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "customer":
            return None
        return int(payload.get("sub"))
    except Exception:
        return None


def _decode_customer_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.CUSTOMER_JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "customer":
            return None
        return payload
    except Exception:
        return None


from fastapi import Header

def get_current_customer(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Customer:
    """从请求头提取客户 JWT"""
    return customer_auth(authorization, db)

def customer_auth(authorization: str = None, db: Session = None) -> Customer:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效 Token")
    token = authorization.replace("Bearer ", "")
    customer_id = _verify_customer_token(token)
    if not customer_id:
        raise HTTPException(status_code=401, detail="Token 无效或已过期，请重新登录")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户账号不存在")
    return customer


def customer_auth_context(authorization: str = None, db: Session = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效 Token")

    token = authorization.replace("Bearer ", "")
    payload = _decode_customer_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 无效或已过期，请重新登录")

    customer_id = payload.get("sub")
    customer = db.query(Customer).filter(Customer.id == int(customer_id)).first() if customer_id else None
    if not customer:
        raise HTTPException(status_code=404, detail="客户账号不存在")

    account_id = payload.get("account_id")
    account = None
    if account_id:
        account = db.query(CustomerAccount).filter(
            CustomerAccount.id == int(account_id),
            CustomerAccount.customer_id == customer.id,
        ).first()
        if not account:
            raise HTTPException(status_code=401, detail="当前子账号不存在，请重新登录")
        if not account.is_active:
            raise HTTPException(status_code=403, detail="当前子账号已停用，请联系主账号管理员")

    return {
        "customer": customer,
        "account": account,
        "account_type": payload.get("account_type") or "CUSTOMER",
    }


def get_current_customer_context(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> dict:
    return customer_auth_context(authorization, db)


def require_portal_account_manager(context: dict = Depends(get_current_customer_context)) -> dict:
    if context["account_type"] == "CUSTOMER":
        return context

    account = context.get("account")
    if not account or account.role not in {"ADMIN", "OWNER"}:
        raise HTTPException(status_code=403, detail="当前账号无权管理子账号，请联系主账号管理员")
    return context


def require_portal_order_signer(context: dict = Depends(get_current_customer_context)) -> dict:
    if context["account_type"] == "CUSTOMER":
        return context

    account = context.get("account")
    if not account or account.role not in {"ADMIN", "OWNER", "SIGNER"}:
        raise HTTPException(status_code=403, detail="当前账号无权执行签字确认")
    return context


# ============ 路由实现 ============

@router.post("/auth/send_code", summary="发送手机验证码（客户登录）")
def send_code(
    phone: str = Body(..., embed=True, description="客户手机号"),
    db: Session = Depends(get_db)
):
    """
    根据手机号查找客户，生成6位验证码并通过短信发送。
    若该手机号未注册为任何客户的 login_phone，则拒绝发送。
    """
    customer = db.query(Customer).filter(Customer.login_phone == phone).first()
    if not customer:
        # 安全起见，不暴露"号码不存在"，统一返回发送成功提示
        return ok(None, msg="若该手机号已关联客户账号，验证码将在1分钟内发出")

    code = "".join(random.choices(string.digits, k=6))
    customer.sms_code = code
    customer.sms_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    send_verify_code_sms(phone, code)

    return ok(None, msg="验证码已发送，请在5分钟内输入")


@router.post("/auth/login", summary="客户登录 (支持密码和验证码)")
def submit_sign(
    payload: dict = Body(..., description="登录参数 (login_type: 'pwd' 或 'sms')"),
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    login_type = payload.get("login_type", "sms")
    customer = None

    if login_type == "pwd":
        username = payload.get("username")
        password = payload.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="请输入账号和密码")

        account = db.query(CustomerAccount).filter(CustomerAccount.username == username).first()
        if account:
            if not account.is_active:
                raise HTTPException(status_code=400, detail="该子账号已停用，请联系主账号管理员")
            if not verify_password(password, account.password_hash):
                raise HTTPException(status_code=400, detail="账号或密码错误")

            customer = db.query(Customer).filter(Customer.id == account.customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="所属客户公司不存在")

            account.last_login_at = datetime.utcnow()
            db.commit()

            token = _generate_customer_token(customer.id, account_id=account.id, account_type="CUSTOMER_ACCOUNT")
            return ok(data={
                "access_token": token,
                "customer_id": customer.id,
                "company_name": customer.company_name,
                "contact_name": account.display_name or account.name,
                "account_id": account.id,
                "account_role": account.role,
                "role_label": customer_account_service.ROLE_LABELS.get(account.role, account.role),
                "account_type": "CUSTOMER_ACCOUNT",
            }, msg="登录成功")

        customer = db.query(Customer).filter(Customer.login_phone == username).first()

        if not customer or password != "123456":
            raise HTTPException(status_code=400, detail="账号或密码错误 (客户主账号测试密码: 123456)")

    else:
        # 短信验证码登录
        phone = payload.get("phone")
        code = payload.get("code")
        
        customer = db.query(Customer).filter(Customer.login_phone == phone).first()
        if not customer or customer.sms_code != code:
            raise HTTPException(status_code=400, detail="验证码错误或已失效")

        if not customer.sms_code_expires_at or datetime.utcnow() > customer.sms_code_expires_at:
            raise HTTPException(status_code=400, detail="验证码已超时，请重新获取")

        # 用完即废
        customer.sms_code = None
        customer.sms_code_expires_at = None
        db.commit()

    token = _generate_customer_token(customer.id, account_type="CUSTOMER")
    return ok(data={
        "access_token": token,
        "customer_id": customer.id,
        "company_name": customer.company_name,
        "contact_name": customer.contact_name,
        "account_role": "OWNER",
        "role_label": customer_account_service.ROLE_LABELS.get("OWNER", "OWNER"),
        "account_type": "CUSTOMER",
    }, msg="登录成功")


@router.get("/me", summary="获取当前客户单位信息")
def get_my_info(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    return ok(data={
        "id": customer.id,
        "company_name": customer.company_name,
        "contact_name": customer.contact_name,
        "contact_phone": customer.contact_phone,
        "address": customer.address,
        "created_at": str(customer.created_at) if hasattr(customer, "created_at") else None
    })


@router.get("/customer/account-center", summary="获取客户账号中心概览")
def get_account_center(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    data = customer_account_service.get_portal_account_center(db, current_customer)
    return ok(data)


@router.get("/account/me", summary="获取当前登录客户账号资料")
def get_portal_current_account(
    context: dict = Depends(get_current_customer_context),
    db: Session = Depends(get_db)
):
    data = customer_account_service.get_portal_current_account(
        db,
        context["customer"],
        context.get("account"),
        context["account_type"],
    )
    return ok(data)


@router.put("/account/me", summary="更新当前登录客户账号资料")
def update_portal_current_account(
    payload: PortalCurrentAccountUpdate,
    context: dict = Depends(get_current_customer_context),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_portal_current_account(
        db,
        context["customer"],
        context.get("account"),
        context["account_type"],
        payload,
    )
    return ok(data, msg="当前账号资料已更新")


@router.put("/account/me/password", summary="修改当前登录客户子账号密码")
def update_portal_current_password(
    payload: PortalCurrentPasswordUpdate,
    context: dict = Depends(get_current_customer_context),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_portal_current_password(
        db,
        context["customer"],
        context.get("account"),
        context["account_type"],
        payload,
    )
    return ok(data, msg="当前账号密码已更新")


@router.put("/customer/account-center/main-account", summary="更新客户主账号信息")
def update_main_account(
    payload: CustomerMainAccountUpdate,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    current_customer = context["customer"]
    data = customer_account_service.update_portal_main_account(db, current_customer, payload)
    return ok(data, msg="主账号信息已更新")


@router.post("/customer/account-center/sub-accounts", summary="创建客户子账号")
def create_sub_account(
    payload: PortalSubAccountCreate,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    current_customer = context["customer"]
    data = customer_account_service.create_portal_sub_account(db, current_customer, payload)
    return ok(data, msg="子账号创建成功")


@router.put("/customer/account-center/sub-accounts/{account_id}", summary="更新客户子账号")
def update_sub_account(
    account_id: int,
    payload: PortalSubAccountUpdate,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_portal_sub_account(db, context["customer"], account_id, payload)
    return ok(data, msg="子账号信息已更新")


@router.put("/customer/account-center/sub-accounts/{account_id}/status", summary="启停客户子账号")
def update_sub_account_status(
    account_id: int,
    payload: CustomerAccountStatusUpdate,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    data = customer_account_service.update_portal_sub_account_status(db, context["customer"], account_id, payload)
    return ok(data, msg="子账号状态已更新")


@router.put("/customer/account-center/sub-accounts/{account_id}/reset-password", summary="重置客户子账号密码")
def reset_sub_account_password(
    account_id: int,
    payload: CustomerAccountPasswordReset,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    data = customer_account_service.reset_portal_sub_account_password(db, context["customer"], account_id, payload)
    return ok(data, msg="子账号密码已重置")


@router.put("/customer/account-center/company-profile", summary="更新客户公司资料")
def update_company_profile(
    payload: CustomerCompanyProfileUpdate,
    context: dict = Depends(require_portal_account_manager),
    db: Session = Depends(get_db)
):
    current_customer = context["customer"]
    data = customer_account_service.update_portal_company_profile(db, current_customer, payload)
    return ok(data, msg="公司资料已更新")


@router.post("/customer/account-center/wechat-bindings", summary="绑定客户微信账号")
def bind_customer_wechat(
    payload: WechatBindingPayload,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    data = customer_account_service.bind_customer_wechat(
        db,
        current_customer,
        scene=payload.scene,
        openid=payload.openid,
        unionid=payload.unionid,
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
    )
    return ok(data, msg="微信绑定成功")


@router.get("/equipments", summary="获取客户设备一览表及状态")
def get_my_equipments(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    from models.equipment import Equipment
    items = db.query(Equipment).filter(Equipment.customer_id == customer.id).all()
    
    result = []
    for e in items:
        # 简单逻辑判断状态：若超过下次检验日期则为异常，否则正常
        status = "正常"
        if e.next_inspection_date and e.next_inspection_date < datetime.now().date():
            status = "待检"
            
        result.append({
            "id": e.id,
            "name": e.name,
            "model_type": e.model_type,
            "category": e.category,
            "tonnage": e.tonnage,
            "status": status,
            "next_inspection_date": str(e.next_inspection_date) if e.next_inspection_date else "未排期"
        })
    return ok(data=result)


@router.get("/stats", summary="获取客户门户首页统计数据")
def get_portal_stats(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    from models.equipment import Equipment
    
    equip_count = db.query(Equipment).filter(Equipment.customer_id == customer.id).count()
    pending_orders = db.query(WorkOrder).filter(
        WorkOrder.customer_id == customer.id,
        WorkOrder.status.in_([OrderStatus.PENDING, OrderStatus.IN_PROGRESS, OrderStatus.PENDING_SIGN])
    ).count()
    
    return ok(data={
        "equipment_count": equip_count,
        "pending_order_count": pending_orders,
        "customer_name": customer.company_name
    })


@router.get("/repairs", summary="客户查看我的维修记录")
def get_customer_repairs(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    from models.repair_order import RepairOrder
    from models.equipment import Equipment
    
    # 查找该客户名下所有设备的维修记录
    repairs = db.query(RepairOrder).join(Equipment).filter(
        Equipment.customer_id == customer.id
    ).order_by(RepairOrder.created_at.desc()).all()
    
    result = []
    for r in repairs:
        result.append({
            "id": r.id,
            "equipment_name": r.equipment.name if r.equipment else "未知设备",
            "fault_symptom": r.fault_symptom,
            "status": r.status,
            "total_fee": float(r.total_fee) if r.total_fee else 0.0,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else None,
            "pdf_report_url": r.pdf_report_url
        })
    return ok(data=result)


@router.get("/orders", summary="客户查看历史工单列表")
def get_customer_orders(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    orders = db.query(WorkOrder).filter(
        WorkOrder.customer_id == customer.id
    ).order_by(WorkOrder.created_at.desc()).all()

    from models.equipment import Equipment
    result = []
    for o in orders:
        equip = db.query(Equipment).filter(Equipment.id == o.equipment_id).first()
        result.append({
            "id": o.id,
            "order_type": o.order_type,
            "status": o.status.value if hasattr(o.status, "value") else o.status,
            "plan_date": str(o.plan_date),
            "equipment_name": equip.name if equip else "—",
            "has_report": bool(o.pdf_report_url)
        })
    return ok(data=result)


@router.get("/orders/{order_id}", summary="客户查看工单详情及报告")
def get_customer_order_detail(
    order_id: int,
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    customer = customer_auth(authorization, db)
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.customer_id == customer.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在或无权限查看")

    return ok(data={
        "id": order.id,
        "order_type": order.order_type,
        "status": order.status.value if hasattr(order.status, "value") else order.status,
        "plan_date": str(order.plan_date),
        "problem_description": order.problem_description,
        "solution": order.solution,
        "sign_url": order.sign_url,
        "pdf_report_url": order.pdf_report_url,
        "checkin_time": str(order.checkin_time) if order.checkin_time else None
    })


@router.post("/orders/{order_id}/sign", summary="客户手写签字确认")
def customer_sign(
    order_id: int,
    sign_url: str = Body(..., embed=True, description="签字图片 URL 或 base64"),
    context: dict = Depends(require_portal_order_signer),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    customer = context["customer"]
    order = db.query(WorkOrder).filter(
        WorkOrder.id == order_id,
        WorkOrder.customer_id == customer.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在或无权限操作")
    if order.status not in (OrderStatus.IN_PROGRESS, OrderStatus.PENDING_SIGN):
        raise HTTPException(status_code=400, detail="该工单当前状态不需要签字")

    order.sign_url = sign_url
    order.status = OrderStatus.COMPLETED
    db.commit()

    # 【二期】触发正式电子签章流水（可选）
    from core.esign import esign_service
    background_tasks.add_task(esign_service.create_flow, order.id, "", [])

    # 触发 PDF 报告生成
    from services.pdf_service import generate_maintenance_report
    background_tasks.add_task(generate_maintenance_report, order.id)

    return ok(None, msg="签字确认成功，维保报告正在生成并归档")
