from sqlalchemy.orm import Session
from schemas.equipment import EquipmentCreate
from repositories.equipment_repository import EquipmentRepository
from models.equipment import Equipment

class EquipmentService:
    def __init__(self, db: Session):
        self.repo = EquipmentRepository(db)

    def create_equipment(self, data: EquipmentCreate, user_id: int) -> Equipment:
        """新建设备并写审计日志"""
        return self.repo.create_equipment(data, user_id)

    def get_equipment_templates(self, category: str, model_type: str):
        return self.repo.get_equipment_templates(category, model_type)

    def get_equipment_detail(self, equipment_id: int):
        equip = self.repo.get_equipment_by_id(equipment_id)
        if equip:
            from models.equipment import EquipmentPart
            parts = self.repo.db.query(EquipmentPart).filter(EquipmentPart.equipment_id == equipment_id).all()
            equip.parts = parts
        return equip

    def update_equipment(self, equipment_id: int, data, user_id: int):
        """更新设备并写审计日志"""
        return self.repo.update_equipment(equipment_id, data, user_id)

    def get_equipment_list(self, search: str = None, customer_id: int = None):
        """获取设备列表，可按名称搜索或按客户过滤"""
        from models.equipment import Equipment
        from models.customer import Customer
        from sqlalchemy import or_
        db = self.repo.db
        query = db.query(Equipment)
        if customer_id:
            query = query.filter(Equipment.customer_id == customer_id)
        if search:
            query = query.filter(Equipment.name.ilike(f"%{search}%"))
        items = query.order_by(Equipment.id.desc()).all()
        # 附带客户名称
        result = []
        for e in items:
            customer = db.query(Customer).filter(Customer.id == e.customer_id).first()
            result.append({
                "id": e.id,
                "name": e.name,
                "model_type": e.model_type,
                "category": e.category,
                "tonnage": e.tonnage,
                "installation_location": e.installation_location,
                "next_inspection_date": str(e.next_inspection_date) if e.next_inspection_date else None,
                "customer_id": e.customer_id,
                "customer_name": customer.company_name if customer else "未知"
            })
        return result
