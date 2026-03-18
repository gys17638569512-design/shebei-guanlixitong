from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.response import ok
from schemas.repair_order import RepairOrderCreate, RepairOrderUpdate, RepairOrderResponse
from models.repair_order import RepairOrder
from models.user import User
from core.permissions import get_current_user
from services import pdf_service

router = APIRouter(
    prefix="/repairs",
    tags=["维修工单管理"]
)


def _is_completed_status(status: str | None) -> bool:
    return status in {"COMPLETED", "已完成"}

@router.post("", summary="新建维修工单")
def create_repair_order(
    payload: RepairOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payload.tech_id and current_user.role == "TECH":
        payload.tech_id = current_user.id
        
    db_order = RepairOrder(**payload.model_dump())
    db.add(db_order)
    db.flush()
    
    from core.audit import write_audit_log
    write_audit_log(db, current_user.id, "CREATE", "repair_orders", db_order.id, payload.model_dump())
    
    db.commit()
    db.refresh(db_order)
    return ok(data=db_order)

@router.get("", summary="获取维修工单列表")
def get_repair_orders(
    status: str = Query(None, description="状态过滤"),
    equipment_id: int = Query(None, description="设备ID过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(RepairOrder)
    if status:
        query = query.filter(RepairOrder.status == status)
    if equipment_id:
        query = query.filter(RepairOrder.equipment_id == equipment_id)
        
    if current_user.role == "TECH":
        query = query.filter(RepairOrder.tech_id == current_user.id)
        
    orders = query.order_by(RepairOrder.created_at.desc()).all()
    # Simple formatting to attach equipment info or serialize
    return ok(data=orders)

@router.get("/{repair_id}", summary="获取维修工单详情")
def get_repair_detail(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(RepairOrder).filter(RepairOrder.id == repair_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="维修工单不存在")
    return ok(data=order)


@router.get("/{repair_id}/report", summary="获取维修工单 PDF 报告")
def get_repair_report(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(RepairOrder).filter(RepairOrder.id == repair_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="维修工单不存在")

    if current_user.role == "TECH" and order.tech_id != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not order.pdf_report_url and _is_completed_status(order.status):
        pdf_service.generate_repair_report(repair_id)
        db.expire_all()
        order = db.query(RepairOrder).filter(RepairOrder.id == repair_id).first()

    if order.pdf_report_url:
        return ok(data={
            "pdf_url": order.pdf_report_url,
            "esign_cert_url": order.esign_cert_url,
        })

    return ok(data={"status": "generating"})

@router.put("/{repair_id}", summary="更新维修工单")
def update_repair_order(
    repair_id: int,
    payload: RepairOrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(RepairOrder).filter(RepairOrder.id == repair_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="维修工单不存在")
        
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(order, k, v)

    if ("labor_fee" in update_data or "other_fee" in update_data) and "total_fee" not in update_data:
        labor_fee = float(order.labor_fee or 0)
        other_fee = float(order.other_fee or 0)
        order.total_fee = labor_fee + other_fee

    if _is_completed_status(order.status) and not order.completed_at:
        order.completed_at = datetime.utcnow()
        
    db.flush()
    from core.audit import write_audit_log
    write_audit_log(db, current_user.id, "UPDATE", "repair_orders", order.id, update_data)
    
    db.commit()
    db.refresh(order)

    if _is_completed_status(order.status) and not order.pdf_report_url:
        background_tasks.add_task(pdf_service.generate_repair_report, order.id)

    return ok(data=order)
