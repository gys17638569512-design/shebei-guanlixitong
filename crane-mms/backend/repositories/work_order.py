from sqlalchemy.orm import Session
from models.work_order import WorkOrder

def get_orders_by_tech_id(db: Session, tech_id: int):
    return db.query(WorkOrder).filter(WorkOrder.technician_id == tech_id).all()

def get_order_by_id(db: Session, order_id: int):
    return db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
