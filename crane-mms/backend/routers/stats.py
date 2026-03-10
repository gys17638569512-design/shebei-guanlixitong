from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.work_order import WorkOrder, OrderStatus
from models.equipment import Equipment
from models.customer import Customer

router = APIRouter(prefix="/stats", tags=["统计中心"])

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
