from sqlalchemy.orm import Session
from models.user import User
from models.work_order import WorkOrder, OrderStatus, InspectionItem
from repositories import work_order as order_repo
from core.exceptions import NotFoundError, ForbiddenError
from core.audit import write_audit_log

def get_my_orders(db: Session, current_user: User) -> list[dict]:
    orders = order_repo.get_orders_by_tech_id(db, current_user.id)
    return [{
        "id": order.id,
        "customer_name": order.customer.company_name,
        "equipment_name": order.equipment.name,
        "plan_date": order.plan_date,
        "status": order.status
    } for order in orders]

def get_order_detail(db: Session, order_id: int, current_user: User) -> dict:
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    
    if current_user.role == "TECH" and order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法查看该工单")
    
    return {
        "id": order.id,
        "customer": {
            "id": order.customer.id,
            "company_name": order.customer.company_name,
            "contact_name": order.customer.contact_name,
            "contact_phone": order.customer.contact_phone
        },
        "equipment": {
            "id": order.equipment.id,
            "name": order.equipment.name,
            "model_type": order.equipment.model_type,
            "category": order.equipment.category
        },
        "technician": {
            "id": order.technician.id,
            "name": order.technician.name
        },
        "plan_date": order.plan_date,
        "status": order.status,
        "checkin_time": order.checkin_time,
        "checkin_address": order.checkin_address,
        "checkin_photo": order.checkin_photo,
        "problem_description": order.problem_description,
        "solution": order.solution,
        "photo_urls": order.photo_urls,
        "sign_url": order.sign_url,
        "pdf_report_url": order.pdf_report_url,
        "esign_cert_url": order.esign_cert_url
    }

def checkin_order(db: Session, order_id: int, checkin_data: dict, current_user: User):
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    
    if order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法操作该工单")
    
    order.status = OrderStatus.IN_PROGRESS
    order.checkin_time = checkin_data.get("checkin_time")
    order.checkin_address = checkin_data.get("checkin_address")
    order.checkin_photo = checkin_data.get("checkin_photo")
    
    write_audit_log(db, current_user.id, "UPDATE", "work_orders", order.id, {"status": order.status, "checkin": True})
    db.commit()

def complete_order(db: Session, order_id: int, completion_data: dict, current_user: User):
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    
    if order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法操作该工单")
    
    if "inspection_items" in completion_data:
        for item_data in completion_data["inspection_items"]:
            item = InspectionItem(
                work_order_id=order_id,
                item_name=item_data["item_name"],
                result=item_data["result"],
                comment=item_data.get("comment"),
                photo_url=item_data.get("photo_url")
            )
            db.add(item)
    
    order.status = OrderStatus.COMPLETED
    order.problem_description = completion_data.get("problem_description")
    order.solution = completion_data.get("solution")
    order.photo_urls = completion_data.get("photo_urls")
    order.sign_url = completion_data.get("sign_url")
    
    write_audit_log(db, current_user.id, "UPDATE", "work_orders", order.id, {"status": order.status})
    db.commit()