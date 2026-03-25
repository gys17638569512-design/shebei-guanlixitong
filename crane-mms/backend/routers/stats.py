from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, desc, or_
from datetime import datetime, timedelta
from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.work_order import WorkOrder, OrderStatus, InspectionItem
from models.equipment import Equipment
from models.customer import Customer
from models.repair_order import RepairOrder
from models.audit_log import AuditLog
from models.user import User

router = APIRouter(prefix="/stats", tags=["统计中心"])

HIGH_RISK_REPAIR_KEYWORDS = (
    "紧急",
    "高危",
    "停机",
    "失灵",
    "冒烟",
    "漏电",
    "断裂",
)


def _enum_value(value):
    return value.value if hasattr(value, "value") else value


def _format_order_summary(order: WorkOrder) -> dict:
    return {
        "id": order.id,
        "order_type": order.order_type,
        "status": _enum_value(order.status),
        "plan_date": str(order.plan_date) if order.plan_date else None,
        "customer_id": order.customer_id,
        "customer_name": order.customer.company_name if order.customer else "未知客户",
        "equipment_id": order.equipment_id,
        "equipment_name": order.equipment.name if order.equipment else "未知设备",
        "technician_id": order.technician_id,
        "technician_name": order.technician.name if order.technician else "未分配",
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
    }


def _format_equipment_warning(equipment: Equipment, today_date) -> dict:
    days_overdue = None
    if equipment.next_inspection_date:
        days_overdue = (today_date - equipment.next_inspection_date).days
    return {
        "equipment_id": equipment.id,
        "equipment_name": equipment.name,
        "equipment_no": getattr(equipment, "equipment_no", None),
        "customer_id": equipment.customer_id,
        "customer_name": equipment.customer.company_name if equipment.customer else "未知客户",
        "category": equipment.category,
        "next_inspection_date": str(equipment.next_inspection_date) if equipment.next_inspection_date else None,
        "days_overdue": max(days_overdue, 0) if days_overdue is not None else None,
        "level": "critical",
    }


def _format_repair_alert(order: RepairOrder) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "equipment_id": order.equipment_id,
        "equipment_name": order.equipment.name if order.equipment else "未知设备",
        "fault_component": order.fault_component,
        "fault_symptom": order.fault_symptom,
        "fault_cause": order.fault_cause,
        "created_at": str(order.created_at) if order.created_at else None,
        "level": "critical",
    }


def _format_abnormal_follow_up(item: InspectionItem) -> dict:
    order = item.work_order
    return {
        "inspection_item_id": item.id,
        "inspection_item_name": item.item_name,
        "inspection_result": item.result,
        "comment": item.comment,
        "order_id": order.id if order else None,
        "order_type": order.order_type if order else None,
        "status": _enum_value(order.status) if order else None,
        "equipment_name": order.equipment.name if order and order.equipment else "未知设备",
        "customer_name": order.customer.company_name if order and order.customer else "未知客户",
    }


def _format_audit_item(log: AuditLog) -> dict:
    risk_level = "high" if log.action in {"DELETE", "BATCH_CREATE"} else "normal"
    return {
        "log_id": log.log_id,
        "user_id": log.user_id,
        "user_name": log.user.name if log.user else "未知用户",
        "action": log.action,
        "table_name": log.table_name,
        "record_id": log.record_id,
        "new_value": log.new_value,
        "level": risk_level,
        "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else None,
    }


def _build_high_risk_repair_filter():
    keyword_filters = []
    for keyword in HIGH_RISK_REPAIR_KEYWORDS:
        keyword_filters.extend(
            [
                RepairOrder.status.like(f"%{keyword}%"),
                RepairOrder.fault_symptom.like(f"%{keyword}%"),
                RepairOrder.fault_cause.like(f"%{keyword}%"),
            ]
        )

    keyword_filters.extend(
        [
            RepairOrder.status.ilike("%urgent%"),
            RepairOrder.fault_symptom.ilike("%urgent%"),
            RepairOrder.fault_cause.ilike("%urgent%"),
            RepairOrder.fault_symptom.ilike("%risk%"),
            RepairOrder.fault_cause.ilike("%risk%"),
        ]
    )
    return or_(*keyword_filters)

@router.get("/dashboard", summary="获取管理端看板核心指标", description="聚合工单计数、设备分布情况及近一周执行趋势数据。")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    # 1. 核心计数指标
    total_orders = db.query(WorkOrder).count()
    pending_orders = db.query(WorkOrder).filter(WorkOrder.status == OrderStatus.PENDING).count()
    ongoing_orders = db.query(WorkOrder).filter(WorkOrder.status.in_([OrderStatus.IN_PROGRESS, "PENDING_SIGN"])).count()
    completed_orders = db.query(WorkOrder).filter(WorkOrder.status == OrderStatus.COMPLETED).count()
    
    total_equipments = db.query(Equipment).count()
    total_customers = db.query(Customer).count()

    # 2. 设备分类分布 (饼图数据)
    category_counts = db.query(Equipment.category, func.count(Equipment.id))\
        .group_by(Equipment.category).all()
    equipment_distribution = [{"name": c or "未分类", "value": count} for c, count in category_counts]

    # 3. 近七日工单执行趋势 (折线图数据)
    seven_days_ago = datetime.utcnow().date() - timedelta(days=6)
    trend_data = db.query(cast(WorkOrder.created_at, Date).label('date'), func.count(WorkOrder.id))\
        .filter(WorkOrder.created_at >= seven_days_ago)\
        .group_by(cast(WorkOrder.created_at, Date))\
        .order_by('date').all()
    
    # 填充缺失日期数据
    trend_dict = {str(d): c for d, c in trend_data}
    filled_trend = []
    for i in range(7):
        curr_date = (seven_days_ago + timedelta(days=i))
        date_str = str(curr_date)
        filled_trend.append({
            "date": curr_date.strftime("%m-%d"),
            "count": trend_dict.get(date_str, 0)
        })

    return ok(data={
        "cards": {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "ongoing_orders": ongoing_orders,
            "completed_orders": completed_orders,
            "total_equipments": total_equipments,
            "total_customers": total_customers
        },
        "equipment_distribution": equipment_distribution,
        "order_trend": filled_trend
    })

@router.get("/notifications", summary="获取全局系统通知")
async def get_notifications(db: Session = Depends(get_db)):
    from models.equipment import Equipment
    from models.part import Part
    from datetime import datetime, timedelta

    # 1. 临期设备 (30天内到期)
    threshold_date = datetime.utcnow().date() + timedelta(days=30)
    expiring_equipments = db.query(Equipment).filter(
        Equipment.next_inspection_date <= threshold_date
    ).all()
    
    # 2. 库存告警 
    low_stock_parts = db.query(Part).filter(
        Part.stock_quantity <= Part.warning_threshold
    ).all()
    
    notifications = []
    
    for eq in expiring_equipments:
        is_overdue = eq.next_inspection_date and eq.next_inspection_date < datetime.utcnow().date()
        notifications.append({
            "id": f"eq_{eq.id}",
            "type": "equipment_expiring",
            "title": "设备检验已过期" if is_overdue else "设备检验临期",
            "message": f"客户【{eq.customer.company_name if eq.customer else '未知'}】的设备【{eq.name}】检验日期为 {eq.next_inspection_date}",
            "date": str(eq.next_inspection_date),
            "level": "danger" if is_overdue else "warning",
            "link": f"/equipments?search={eq.equipment_no}"
        })
        
    for p in low_stock_parts:
        notifications.append({
            "id": f"pt_{p.id}",
            "type": "part_low_stock",
            "title": "备件库存不足",
            "message": f"备件【{p.name}】当前库存 {p.stock_quantity} {p.unit}，已低于警戒值 {p.warning_threshold} {p.unit}",
            "level": "warning",
            "link": "/system/parts"
        })
        
    return ok(data=notifications)


@router.get(
    "/workbench",
    summary="获取管理首页工作台聚合数据",
    description="面向管理中台首页，聚合高危预警、今日待办、核心指标、排期信息与最近审计记录。",
)
async def get_workbench_stats(
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db),
):
    today_date = datetime.utcnow().date()
    warning_threshold = today_date + timedelta(days=30)

    overdue_equipment_query = db.query(Equipment).filter(
        Equipment.next_inspection_date.isnot(None),
        Equipment.next_inspection_date < today_date,
    )
    due_soon_equipment_query = db.query(Equipment).filter(
        Equipment.next_inspection_date.isnot(None),
        Equipment.next_inspection_date >= today_date,
        Equipment.next_inspection_date <= warning_threshold,
    )
    high_risk_repair_query = (
        db.query(RepairOrder)
        .filter(RepairOrder.status.notin_(["已完成", "COMPLETED"]))
        .filter(_build_high_risk_repair_filter())
    )

    overdue_equipment_count = overdue_equipment_query.count()
    due_soon_equipment_count = due_soon_equipment_query.count()
    high_risk_order_count = high_risk_repair_query.count()
    today_order_count = db.query(func.count(WorkOrder.id)).filter(WorkOrder.plan_date == today_date).scalar() or 0
    in_progress_order_count = (
        db.query(func.count(WorkOrder.id))
        .filter(WorkOrder.status.in_([OrderStatus.IN_PROGRESS, OrderStatus.PENDING_SIGN]))
        .scalar()
        or 0
    )
    completed_order_count = db.query(func.count(WorkOrder.id)).filter(WorkOrder.status == OrderStatus.COMPLETED).scalar() or 0
    equipment_total = db.query(func.count(Equipment.id)).scalar() or 0
    customer_total = db.query(func.count(Customer.id)).scalar() or 0
    warning_equipment_count = overdue_equipment_count + due_soon_equipment_count

    overdue_equipments = (
        overdue_equipment_query
        .order_by(Equipment.next_inspection_date.asc())
        .limit(10)
        .all()
    )
    due_soon_equipments = (
        due_soon_equipment_query
        .order_by(Equipment.next_inspection_date.asc())
        .limit(10)
        .all()
    )

    high_risk_repairs = (
        high_risk_repair_query
        .order_by(desc(RepairOrder.created_at))
        .limit(10)
        .all()
    )

    pending_dispatch_orders = (
        db.query(WorkOrder)
        .filter(WorkOrder.status == OrderStatus.PENDING)
        .order_by(WorkOrder.plan_date.asc(), WorkOrder.created_at.asc())
        .limit(10)
        .all()
    )
    pending_report_confirmation_orders = (
        db.query(WorkOrder)
        .filter(WorkOrder.status == OrderStatus.PENDING_SIGN)
        .order_by(WorkOrder.updated_at.desc(), WorkOrder.created_at.desc())
        .limit(10)
        .all()
    )
    abnormal_follow_up_items = (
        db.query(InspectionItem)
        .join(InspectionItem.work_order)
        .filter(InspectionItem.result == "ABNORMAL")
        .order_by(desc(WorkOrder.updated_at), desc(InspectionItem.id))
        .limit(10)
        .all()
    )
    today_orders = (
        db.query(WorkOrder)
        .filter(WorkOrder.plan_date == today_date)
        .order_by(WorkOrder.created_at.asc(), WorkOrder.id.asc())
        .all()
    )
    recent_audits = (
        db.query(AuditLog)
        .order_by(desc(AuditLog.created_at))
        .limit(8)
        .all()
    )

    data = {
        "alerts": {
            "summary": {
                "overdue_equipments": overdue_equipment_count,
                "high_risk_orders": high_risk_order_count,
            },
            "overdue_equipments": [_format_equipment_warning(item, today_date) for item in overdue_equipments],
            "high_risk_orders": [_format_repair_alert(item) for item in high_risk_repairs],
        },
        "todos": {
            "pending_dispatch": [_format_order_summary(item) for item in pending_dispatch_orders],
            "pending_report_confirmation": [_format_order_summary(item) for item in pending_report_confirmation_orders],
            "abnormal_follow_ups": [_format_abnormal_follow_up(item) for item in abnormal_follow_up_items],
            "approvals": [],
        },
        "metrics": {
            "today_order_count": today_order_count,
            "in_progress_order_count": in_progress_order_count,
            "completed_order_count": completed_order_count,
            "equipment_total": equipment_total,
            "customer_total": customer_total,
            "warning_equipment_count": warning_equipment_count,
        },
        "schedule": {
            "date": str(today_date),
            "today_orders": [_format_order_summary(item) for item in today_orders],
            "upcoming_inspections": [
                {
                    "equipment_id": item.id,
                    "equipment_name": item.name,
                    "customer_name": item.customer.company_name if item.customer else "未知客户",
                    "next_inspection_date": str(item.next_inspection_date) if item.next_inspection_date else None,
                }
                for item in due_soon_equipments
            ],
        },
        "quick_actions": [
            {"key": "create_order", "label": "新建派单", "path": "/orders/create"},
            {"key": "reports_archive", "label": "待确认报告", "path": "/orders/reports/archive"},
            {"key": "warning_center", "label": "合规预警", "path": "/stats/workbench"},
        ],
        "recent_audits": [_format_audit_item(item) for item in recent_audits],
        "warning_summary": {
            "overdue_inspection_count": overdue_equipment_count,
            "inspection_due_soon_count": due_soon_equipment_count,
            "high_risk_order_count": high_risk_order_count,
        },
    }
    return ok(data=data)
