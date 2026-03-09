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
