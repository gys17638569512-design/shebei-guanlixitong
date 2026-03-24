import json

from sqlalchemy.orm import Session
from schemas.equipment import EquipmentCreate
from repositories.equipment_repository import EquipmentRepository
from models.equipment import Equipment
from services.equipment_template_service import EquipmentTemplateService

class EquipmentService:
    def __init__(self, db: Session):
        self.repo = EquipmentRepository(db)
        self.template_service = EquipmentTemplateService(db)

    def create_equipment(self, data: EquipmentCreate, user_id: int) -> Equipment:
        """新建设备并写审计日志"""
        equipment = self.repo.create_equipment(data, user_id)
        if data.submit_as_template_candidate:
            self.template_service.create_candidate_from_equipment(equipment, user_id)
        return self.serialize_equipment(equipment)

    def get_equipment_templates(self, category: str, model_type: str):
        return self.repo.get_equipment_templates(category, model_type)

    def get_equipment_detail(self, equipment_id: int):
        equip = self.repo.get_equipment_by_id(equipment_id)
        if equip:
            from models.equipment import EquipmentPart
            parts = self.repo.db.query(EquipmentPart).filter(EquipmentPart.equipment_id == equipment_id).all()
            equip.parts = parts
            return self.serialize_equipment(equip)
        return None

    def update_equipment(self, equipment_id: int, data, user_id: int):
        """更新设备并写审计日志"""
        equipment = self.repo.update_equipment(equipment_id, data, user_id)
        if not equipment:
            return None
        return self.serialize_equipment(equipment)

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
                "manufacturer": e.manufacturer,
                "tonnage": e.tonnage,
                "installation_location": e.installation_location,
                "next_inspection_date": str(e.next_inspection_date) if e.next_inspection_date else None,
                "customer_id": e.customer_id,
                "customer_name": customer.company_name if customer else "未知",
                "customer": {"company_name": customer.company_name if customer else "未知"},
            })
        return result

    def serialize_equipment(self, equip: Equipment):
        return {
            "id": equip.id,
            "customer_id": equip.customer_id,
            "category": equip.category,
            "model_type": equip.model_type,
            "name": equip.name,
            "manufacturer": equip.manufacturer,
            "tonnage": equip.tonnage,
            "span": equip.span,
            "lifting_height": equip.lifting_height,
            "work_class": equip.work_class,
            "installation_location": equip.installation_location,
            "last_inspection_date": str(equip.last_inspection_date) if equip.last_inspection_date else None,
            "next_inspection_date": str(equip.next_inspection_date) if equip.next_inspection_date else None,
            "warranty_end_date": str(equip.warranty_end_date) if equip.warranty_end_date else None,
            "applied_template_id": equip.applied_template_id,
            "applied_template_version": equip.applied_template_version,
            "submit_as_template_candidate": bool(equip.submit_as_template_candidate),
            "inspection_items": json.loads(equip.inspection_items_json) if equip.inspection_items_json else [],
            "parts": [
                {
                    "id": part.id,
                    "equipment_id": part.equipment_id,
                    "part_name": part.part_name,
                    "specification": part.specification,
                    "quantity": part.quantity,
                }
                for part in getattr(equip, "parts", []) or []
            ],
        }
