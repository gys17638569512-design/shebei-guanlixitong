from sqlalchemy.orm import Session

from core.audit import write_audit_log
from core.exceptions import BusinessError, NotFoundError
from core.security import get_password_hash
from models.customer import Customer
from models.customer_account import CustomerAccount
from models.customer_profile import CustomerProfile
from models.wechat_binding import WechatBinding
from schemas.customer_account import (
    CustomerAccountPasswordReset,
    CustomerAccountCreate,
    CustomerAccountStatusUpdate,
    CustomerAccountUpdate,
    CustomerCompanyProfileUpdate,
    CustomerMainAccountUpdate,
    PortalCurrentAccountUpdate,
    PortalCurrentPasswordUpdate,
    PortalSubAccountCreate,
    PortalSubAccountUpdate,
)


ROLE_LABELS = {
    "OWNER": "主账号",
    "ADMIN": "管理员",
    "SIGNER": "签字人",
    "VIEWER": "查看人",
    "REPORTER": "报修人",
    "MEMBER": "成员",
}


def _build_portal_permissions(account_type: str, account: CustomerAccount | None = None) -> dict:
    role = "OWNER" if account_type == "CUSTOMER" else (account.role if account else "VIEWER")
    return {
        "account_role": role,
        "role_label": ROLE_LABELS.get(role, role),
        "can_manage_accounts": account_type == "CUSTOMER" or role in {"ADMIN", "OWNER"},
        "can_sign_orders": account_type == "CUSTOMER" or role in {"ADMIN", "OWNER", "SIGNER"},
    }


def _mask_phone(phone: str | None) -> str | None:
    if not phone or len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def _get_customer_or_raise(db: Session, customer_id: int) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundError("客户公司不存在")
    return customer


def _get_customer_account_or_raise(db: Session, customer_id: int, account_id: int) -> CustomerAccount:
    account = db.query(CustomerAccount).filter(
        CustomerAccount.id == account_id,
        CustomerAccount.customer_id == customer_id,
    ).first()
    if not account:
        raise NotFoundError("客户子账号不存在")
    return account


def _get_or_create_profile(db: Session, customer: Customer) -> CustomerProfile:
    profile = db.query(CustomerProfile).filter(CustomerProfile.customer_id == customer.id).first()
    if profile:
        return profile

    profile = CustomerProfile(
        customer_id=customer.id,
        short_name=customer.company_name,
        status="已开通",
        portal_mode="Web 完整版 + 微信核心版",
    )
    db.add(profile)
    db.flush()
    return profile


def _get_owner_account(db: Session, customer_id: int) -> CustomerAccount | None:
    return db.query(CustomerAccount).filter(
        CustomerAccount.customer_id == customer_id,
        CustomerAccount.is_owner == True,
    ).first()


def _build_binding_map(db: Session, owner_type: str, owner_ids: list[int]) -> dict[int, WechatBinding]:
    if not owner_ids:
        return {}
    bindings = db.query(WechatBinding).filter(
        WechatBinding.owner_type == owner_type,
        WechatBinding.owner_id.in_(owner_ids),
        WechatBinding.is_active == True,
    ).all()
    return {binding.owner_id: binding for binding in bindings}


def _serialize_company_profile(customer: Customer, profile: CustomerProfile) -> dict:
    short_name = profile.short_name or customer.company_name
    return {
        "customer_id": customer.id,
        "company_name": customer.company_name,
        "short_name": short_name,
        "company_code": profile.company_code,
        "logo_url": profile.logo_url,
        "logo_text": (short_name or "客")[:1],
        "industry": profile.industry,
        "contact_name": customer.contact_name,
        "contact_phone": customer.contact_phone,
        "address": customer.address,
        "status": profile.status,
        "portal_mode": profile.portal_mode,
        "remark": profile.remark,
    }


def _serialize_customer_account(account: CustomerAccount, binding: WechatBinding | None = None, mask_phone: bool = False) -> dict:
    phone = _mask_phone(account.phone) if mask_phone else account.phone
    return {
        "id": account.id,
        "customer_id": account.customer_id,
        "parent_account_id": account.parent_account_id,
        "role": account.role,
        "role_label": ROLE_LABELS.get(account.role, account.role),
        "username": account.username,
        "name": account.name,
        "display_name": account.display_name or account.name,
        "phone": phone,
        "phone_raw": account.phone,
        "email": account.email,
        "avatar_url": account.avatar_url,
        "is_owner": account.is_owner,
        "is_active": account.is_active,
        "must_change_password": account.must_change_password,
        "status_label": "启用" if account.is_active else "停用",
        "wechat_status": "已绑定" if binding else "未绑定",
        "last_login_at": account.last_login_at.strftime("%Y-%m-%d %H:%M") if account.last_login_at else "未登录",
        "created_at": account.created_at.strftime("%Y-%m-%d %H:%M") if account.created_at else None,
        "updated_at": account.updated_at.strftime("%Y-%m-%d %H:%M") if account.updated_at else None,
    }


def _serialize_main_account_from_customer(customer: Customer, binding: WechatBinding | None = None) -> dict:
    return {
        "display_name": customer.contact_name,
        "username": customer.login_phone or f"customer-{customer.id}",
        "phone": _mask_phone(customer.contact_phone),
        "wechat_status": "已绑定" if binding else "未绑定",
        "login_mode": "账号密码 / 微信",
        "last_login_at": "未记录",
        "created_at": None,
        "permissions": ["查看设备", "签字确认", "子账号管理", "快速报修"],
    }


def list_customer_accounts(db: Session, customer_id: int, mask_phone: bool = False) -> list[dict]:
    _get_customer_or_raise(db, customer_id)
    accounts = db.query(CustomerAccount).filter(
        CustomerAccount.customer_id == customer_id
    ).order_by(CustomerAccount.is_owner.desc(), CustomerAccount.id.asc()).all()
    binding_map = _build_binding_map(db, "CUSTOMER_ACCOUNT", [account.id for account in accounts])
    return [
        _serialize_customer_account(account, binding_map.get(account.id), mask_phone=mask_phone)
        for account in accounts
    ]


def create_customer_account(db: Session, payload: CustomerAccountCreate, operator_id: int | None = None, created_by_type: str = "PLATFORM_USER") -> dict:
    _get_customer_or_raise(db, payload.customer_id)
    if db.query(CustomerAccount).filter(CustomerAccount.username == payload.username).first():
        raise BusinessError("客户账号登录名已存在")

    if payload.is_owner and _get_owner_account(db, payload.customer_id):
        raise BusinessError("该客户公司已存在主账号")

    account = CustomerAccount(
        customer_id=payload.customer_id,
        parent_account_id=payload.parent_account_id,
        role=payload.role,
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        name=payload.name,
        display_name=payload.display_name,
        phone=payload.phone,
        email=payload.email,
        avatar_url=payload.avatar_url,
        is_owner=payload.is_owner,
        is_active=payload.is_active,
        must_change_password=True,
        created_by_type=created_by_type,
        created_by_id=operator_id,
    )
    db.add(account)
    db.flush()

    if operator_id:
        write_audit_log(
            db=db,
            user_id=operator_id,
            action="CREATE",
            table_name="customer_accounts",
            record_id=account.id,
            new_value={"customer_id": account.customer_id, "username": account.username, "role": account.role},
        )

    db.commit()
    db.refresh(account)
    return _serialize_customer_account(account)


def update_customer_account(db: Session, account_id: int, payload: CustomerAccountUpdate, operator_id: int | None = None) -> dict:
    account = db.query(CustomerAccount).filter(CustomerAccount.id == account_id).first()
    if not account:
        raise NotFoundError("客户账号不存在")

    update_data = payload.model_dump(exclude_unset=True)
    if "username" in update_data and update_data["username"] != account.username:
        if db.query(CustomerAccount).filter(CustomerAccount.username == update_data["username"]).first():
            raise BusinessError("客户账号登录名已存在")

    if update_data.get("is_owner") and not account.is_owner:
        owner = _get_owner_account(db, account.customer_id)
        if owner and owner.id != account.id:
            raise BusinessError("该客户公司已存在主账号")

    for key, value in update_data.items():
        setattr(account, key, value)

    db.flush()
    if operator_id:
        write_audit_log(
            db=db,
            user_id=operator_id,
            action="UPDATE",
            table_name="customer_accounts",
            record_id=account.id,
            new_value={"customer_id": account.customer_id, **update_data},
        )

    db.commit()
    db.refresh(account)
    return _serialize_customer_account(account)


def get_customer_company_profile(db: Session, customer_id: int) -> dict:
    customer = _get_customer_or_raise(db, customer_id)
    profile = _get_or_create_profile(db, customer)
    db.commit()
    return _serialize_company_profile(customer, profile)


def update_customer_company_profile(db: Session, customer_id: int, payload: CustomerCompanyProfileUpdate, operator_id: int | None = None) -> dict:
    customer = _get_customer_or_raise(db, customer_id)
    profile = _get_or_create_profile(db, customer)
    update_data = payload.model_dump(exclude_unset=True)

    customer_fields = {"company_name", "contact_name", "contact_phone", "address"}
    for key in list(update_data.keys()):
        if key in customer_fields:
            setattr(customer, key, update_data.pop(key))

    for key, value in update_data.items():
        setattr(profile, key, value)

    db.flush()
    if operator_id:
        write_audit_log(
            db=db,
            user_id=operator_id,
            action="UPDATE",
            table_name="customers",
            record_id=customer.id,
            new_value=_serialize_company_profile(customer, profile),
        )

    db.commit()
    db.refresh(customer)
    db.refresh(profile)
    return _serialize_company_profile(customer, profile)


def get_portal_account_center(db: Session, customer: Customer) -> dict:
    profile = _get_or_create_profile(db, customer)
    owner_account = _get_owner_account(db, customer.id)
    sub_accounts = db.query(CustomerAccount).filter(
        CustomerAccount.customer_id == customer.id,
        CustomerAccount.is_owner == False,
    ).order_by(CustomerAccount.id.asc()).all()

    binding_map = _build_binding_map(
        db,
        "CUSTOMER_ACCOUNT",
        [account.id for account in sub_accounts] + ([owner_account.id] if owner_account else []),
    )
    customer_binding = _build_binding_map(db, "CUSTOMER", [customer.id]).get(customer.id)

    if owner_account:
        main_account = _serialize_customer_account(owner_account, binding_map.get(owner_account.id), mask_phone=True)
        main_account["permissions"] = ["查看设备", "签字确认", "子账号管理", "快速报修"]
        main_account["login_mode"] = "账号密码 / 微信"
    else:
        main_account = _serialize_main_account_from_customer(customer, customer_binding)

    return {
        "mainAccount": main_account,
        "subAccounts": [_serialize_customer_account(account, binding_map.get(account.id), mask_phone=True) for account in sub_accounts],
        "companyProfile": _serialize_company_profile(customer, profile),
    }


def update_portal_main_account(db: Session, customer: Customer, payload: CustomerMainAccountUpdate) -> dict:
    owner_account = _get_owner_account(db, customer.id)
    update_data = payload.model_dump(exclude_unset=True)

    if owner_account:
        for key, value in update_data.items():
            setattr(owner_account, key, value)
    else:
        if "name" in update_data:
            customer.contact_name = update_data["name"]
        if "phone" in update_data:
            customer.contact_phone = update_data["phone"]
            customer.login_phone = update_data["phone"]

    db.commit()
    return get_portal_account_center(db, customer)["mainAccount"]


def create_portal_sub_account(db: Session, customer: Customer, payload: PortalSubAccountCreate) -> dict:
    account_payload = CustomerAccountCreate(
        customer_id=customer.id,
        parent_account_id=None,
        role=payload.role,
        username=payload.username,
        name=payload.name,
        display_name=payload.display_name,
        phone=payload.phone,
        email=payload.email,
        avatar_url=payload.avatar_url,
        is_owner=False,
        is_active=True,
        password=payload.password,
    )
    return create_customer_account(db, account_payload, operator_id=None, created_by_type="CUSTOMER_ACCOUNT")


def update_portal_sub_account(db: Session, customer: Customer, account_id: int, payload: PortalSubAccountUpdate) -> dict:
    account = _get_customer_account_or_raise(db, customer.id, account_id)
    if account.is_owner:
        raise BusinessError("客户主账号请在主账号资料中维护")

    update_data = payload.model_dump(exclude_unset=True)
    if "username" in update_data and update_data["username"] != account.username:
        if db.query(CustomerAccount).filter(CustomerAccount.username == update_data["username"]).first():
            raise BusinessError("客户账号登录名已存在")

    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    binding_map = _build_binding_map(db, "CUSTOMER_ACCOUNT", [account.id])
    return _serialize_customer_account(account, binding_map.get(account.id), mask_phone=True)


def update_portal_sub_account_status(db: Session, customer: Customer, account_id: int, payload: CustomerAccountStatusUpdate) -> dict:
    account = _get_customer_account_or_raise(db, customer.id, account_id)
    if account.is_owner:
        raise BusinessError("客户主账号不支持在子账号列表中启停")

    account.is_active = payload.is_active
    db.commit()
    db.refresh(account)
    binding_map = _build_binding_map(db, "CUSTOMER_ACCOUNT", [account.id])
    return _serialize_customer_account(account, binding_map.get(account.id), mask_phone=True)


def reset_portal_sub_account_password(db: Session, customer: Customer, account_id: int, payload: CustomerAccountPasswordReset) -> dict:
    account = _get_customer_account_or_raise(db, customer.id, account_id)
    if account.is_owner:
        raise BusinessError("客户主账号请在主账号资料中修改密码")

    account.password_hash = get_password_hash(payload.password)
    account.must_change_password = True
    db.commit()
    db.refresh(account)
    binding_map = _build_binding_map(db, "CUSTOMER_ACCOUNT", [account.id])
    return _serialize_customer_account(account, binding_map.get(account.id), mask_phone=True)


def update_portal_company_profile(db: Session, customer: Customer, payload: CustomerCompanyProfileUpdate) -> dict:
    return update_customer_company_profile(db, customer.id, payload, operator_id=None)


def bind_customer_wechat(
    db: Session,
    customer: Customer,
    scene: str,
    openid: str,
    unionid: str | None = None,
    nickname: str | None = None,
    avatar_url: str | None = None,
) -> dict:
    binding = db.query(WechatBinding).filter(
        WechatBinding.owner_type == "CUSTOMER",
        WechatBinding.owner_id == customer.id,
        WechatBinding.scene == scene,
    ).first()

    if binding:
        binding.openid = openid
        binding.unionid = unionid
        binding.nickname = nickname
        binding.avatar_url = avatar_url
        binding.bound_mobile = customer.contact_phone
        binding.is_active = True
        binding.unbound_at = None
    else:
        binding = WechatBinding(
            owner_type="CUSTOMER",
            owner_id=customer.id,
            scene=scene,
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url,
            bound_mobile=customer.contact_phone,
            is_active=True,
        )
        db.add(binding)

    db.commit()
    return {
        "scene": binding.scene,
        "owner_type": binding.owner_type,
        "owner_id": binding.owner_id,
        "openid": binding.openid,
        "nickname": binding.nickname,
        "avatar_url": binding.avatar_url,
        "bound_mobile": binding.bound_mobile,
        "is_active": binding.is_active,
        "bound_at": binding.bound_at.strftime("%Y-%m-%d %H:%M:%S") if binding.bound_at else None,
    }


def get_portal_current_account(db: Session, customer: Customer, account: CustomerAccount | None = None, account_type: str = "CUSTOMER") -> dict:
    permissions = _build_portal_permissions(account_type, account)
    profile = _get_or_create_profile(db, customer)

    if account_type == "CUSTOMER_ACCOUNT" and account:
        return {
            "account_type": account_type,
            "account_id": account.id,
            "username": account.username,
            "name": account.name,
            "display_name": account.display_name or account.name,
            "phone": account.phone,
            "email": account.email,
            "company_name": customer.company_name,
            "company_logo_url": profile.logo_url if profile else None,
            "must_change_password": account.must_change_password,
            "is_active": account.is_active,
            "last_login_at": account.last_login_at.strftime("%Y-%m-%d %H:%M") if account.last_login_at else None,
            **permissions,
        }

    return {
        "account_type": "CUSTOMER",
        "account_id": None,
        "username": customer.login_phone or f"customer-{customer.id}",
        "name": customer.contact_name,
        "display_name": customer.contact_name,
        "phone": customer.contact_phone,
        "email": None,
        "company_name": customer.company_name,
        "company_logo_url": profile.logo_url if profile else None,
        "must_change_password": False,
        "is_active": True,
        "last_login_at": None,
        **permissions,
    }


def update_portal_current_account(
    db: Session,
    customer: Customer,
    account: CustomerAccount | None,
    account_type: str,
    payload: PortalCurrentAccountUpdate,
) -> dict:
    update_data = payload.model_dump(exclude_unset=True)

    if account_type == "CUSTOMER_ACCOUNT" and account:
        for field in ("name", "display_name", "phone", "email"):
            if field in update_data:
                setattr(account, field, update_data[field])
        db.commit()
        db.refresh(account)
        return get_portal_current_account(db, customer, account, account_type)

    if "name" in update_data:
        customer.contact_name = update_data["name"]
    elif "display_name" in update_data:
        customer.contact_name = update_data["display_name"]
    if "phone" in update_data:
        customer.contact_phone = update_data["phone"]
        customer.login_phone = update_data["phone"]

    db.commit()
    db.refresh(customer)
    return get_portal_current_account(db, customer, None, "CUSTOMER")


def update_portal_current_password(
    db: Session,
    customer: Customer,
    account: CustomerAccount | None,
    account_type: str,
    payload: PortalCurrentPasswordUpdate,
) -> dict:
    if account_type != "CUSTOMER_ACCOUNT" or not account:
        raise BusinessError("客户主账号改密能力待独立登录密码方案上线后开放")

    account.password_hash = get_password_hash(payload.password)
    account.must_change_password = False
    db.commit()
    db.refresh(account)
    return get_portal_current_account(db, customer, account, account_type)
