from sqlalchemy.orm import Session
from models.user import User
from models.work_order import WorkOrder, OrderStatus, InspectionItem, WorkOrderPart
from models.part import Part
from repositories import work_order as order_repo
from core.exceptions import NotFoundError, ForbiddenError, BusinessError
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
        "esign_cert_url": order.esign_cert_url,
        "used_parts": [{
            "part_id": p.part.id,
            "part_no": p.part.part_no,
            "name": p.part.name,
            "specification": p.part.specification,
            "quantity": p.quantity
        } for p in order.used_parts] if getattr(order, 'used_parts', None) else []
    }

import dateutil.parser

def checkin_order(db: Session, order_id: int, checkin_data: dict, current_user: User):
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    
    if order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法操作该工单")
        
    if order.status != OrderStatus.PENDING:
        raise ForbiddenError("当前状态不允许打卡，工单未处于待派发/待处理状态")
    
    order.status = OrderStatus.IN_PROGRESS
    
    ctime_str = checkin_data.get("checkin_time")
    if ctime_str:
        order.checkin_time = dateutil.parser.isoparse(ctime_str).replace(tzinfo=None)
        
    order.checkin_address = checkin_data.get("checkin_address")
    order.checkin_photo = checkin_data.get("checkin_photo")
    
    write_audit_log(db, current_user.id, "UPDATE", "work_orders", order.id, {"status": str(order.status), "checkin": True})
    db.commit()

def push_for_sign(db: Session, order_id: int, push_data: dict, current_user: User):
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    if order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法操作该工单")
    if order.status != OrderStatus.IN_PROGRESS:
        raise ForbiddenError("当前状态不允许推送签字，需先完成现场打卡")
        
    order.status = OrderStatus.PENDING_SIGN
    order.problem_description = push_data.get("problem_description")
    order.solution = push_data.get("solution")
    
    photo_urls = push_data.get("photo_urls")
    if isinstance(photo_urls, list):
        import json
        order.photo_urls = json.dumps(photo_urls, ensure_ascii=False)
    else:
        order.photo_urls = photo_urls
    
    if "inspection_items" in push_data:
        for item_data in push_data["inspection_items"]:
            new_item = InspectionItem(
                work_order_id=order.id,
                item_name=item_data["item_name"],
                result=item_data["result"],
                comment=item_data.get("comment", ""),
                photo_url=item_data.get("photo_url")
            )
            db.add(new_item)
            
    # 【新增】备件使用扣减逻辑 (仅在 PENDING_SIGN 即第一次流转保存时固化防篡改)
    if "used_parts" in push_data:
        for p_data in push_data["used_parts"]:
            part_id = p_data.get("part_id")
            quantity = p_data.get("quantity", 1)
            
            part = db.query(Part).filter(Part.id == part_id).with_for_update().first()
            if not part:
                raise NotFoundError(f"未找到可用备件(ID:{part_id})")
            if part.stock_quantity < quantity:
                raise BusinessError(f"备件【{part.name}】库存不足，当前仅剩 {part.stock_quantity} 件")
                
            # 扣减库存 & 记录挂载
            part.stock_quantity -= quantity
            db.add(WorkOrderPart(work_order_id=order.id, part_id=part.id, quantity=quantity))
            
    write_audit_log(db, current_user.id, "UPDATE", "work_orders", order.id, {"status": str(order.status), "pushed": True})
    db.commit()

def complete_order(db: Session, order_id: int, completion_data: dict, current_user: User):
    order = order_repo.get_order_by_id(db, order_id)
    if not order:
        raise NotFoundError("工单不存在")
    
    if order.technician_id != current_user.id:
        raise ForbiddenError("权限不足，无法操作该工单")

    if order.status not in (OrderStatus.IN_PROGRESS, OrderStatus.PENDING_SIGN):
        raise ForbiddenError("当前状态不允许结单，需先完成现场打卡环节")

    if not completion_data.get("sign_url"):
        raise ForbiddenError("必须携带客户电子手写签字才能完成结单")
    
    if order.status == OrderStatus.IN_PROGRESS:
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
                
        # 【新增】当面签字一指流直达的备件使用扣减库出账
        if "used_parts" in completion_data:
            for p_data in completion_data["used_parts"]:
                part_id = p_data.get("part_id")
                quantity = p_data.get("quantity", 1)
                
                part = db.query(Part).filter(Part.id == part_id).with_for_update().first()
                if not part:
                    raise NotFoundError(f"缺少入账备件(ID:{part_id})")
                if part.stock_quantity < quantity:
                    raise BusinessError(f"库房备件【{part.name}】存量吃紧，当前仅剩 {part.stock_quantity} 件")
                    
                part.stock_quantity -= quantity
                db.add(WorkOrderPart(work_order_id=order.id, part_id=part.id, quantity=quantity))
                
        order.problem_description = completion_data.get("problem_description")
        order.solution = completion_data.get("solution")
        
        photo_urls = completion_data.get("photo_urls")
        if isinstance(photo_urls, list):
            import json
            order.photo_urls = json.dumps(photo_urls, ensure_ascii=False)
        else:
            order.photo_urls = photo_urls
    
    order.status = OrderStatus.COMPLETED
    order.sign_url = completion_data.get("sign_url")
    
    write_audit_log(db, current_user.id, "UPDATE", "work_orders", order.id, {"status": str(order.status)})
    db.commit()