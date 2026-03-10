from sqlalchemy.orm import Session, joinedload
from models.work_order import WorkOrder

def get_orders_with_relations(db: Session, status=None, technician_id=None, customer_id=None):
    """
    使用 joinedload 一次性加载工单及关联的客户、设备、工程师数据，避免 N+1 查询。
    """
    query = db.query(WorkOrder).options(
        joinedload(WorkOrder.customer),
        joinedload(WorkOrder.equipment),
        joinedload(WorkOrder.technician),
    )
    if status:
        query = query.filter(WorkOrder.status == status)
    if technician_id:
        query = query.filter(WorkOrder.technician_id == technician_id)
    if customer_id:
        query = query.filter(WorkOrder.customer_id == customer_id)
    
    return query.order_by(WorkOrder.created_at.desc()).all()
