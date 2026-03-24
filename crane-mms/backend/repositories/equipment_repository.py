import json

from sqlalchemy.orm import Session
from models.equipment import Equipment, EquipmentPart
from schemas.equipment import EquipmentCreate
from core.audit import write_audit_log

class EquipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_equipment(self, equip_data: EquipmentCreate, user_id: int) -> Equipment:
        # Create the main equipment record
        db_equip = Equipment(
            customer_id=equip_data.customer_id,
            category=equip_data.category,
            model_type=equip_data.model_type,
            name=equip_data.name,
            manufacturer=equip_data.manufacturer,
            tonnage=equip_data.tonnage,
            span=equip_data.span,
            lifting_height=equip_data.lifting_height,
            work_class=equip_data.work_class,
            installation_location=equip_data.installation_location,
            last_inspection_date=equip_data.last_inspection_date,
            next_inspection_date=equip_data.next_inspection_date,
            warranty_end_date=equip_data.warranty_end_date,
            applied_template_id=equip_data.applied_template_id,
            applied_template_version=equip_data.applied_template_version,
            submit_as_template_candidate=equip_data.submit_as_template_candidate,
            inspection_items_json=json.dumps(equip_data.inspection_items or [], ensure_ascii=False),
        )
        self.db.add(db_equip)
        self.db.flush()

        # Add associated parts if any
        if equip_data.parts:
            for part in equip_data.parts:
                db_part = EquipmentPart(
                    equipment_id=db_equip.id,
                    part_name=part.part_name,
                    specification=part.specification,
                    quantity=part.quantity
                )
                self.db.add(db_part)

        # 写入操作审计日志 - PRD 铁律：所有写操作必须记录
        write_audit_log(
            db=self.db,
            user_id=user_id,
            action="CREATE",
            table_name="equipments",
            record_id=db_equip.id,
            new_value={"name": db_equip.name, "customer_id": db_equip.customer_id, "category": db_equip.category, "manufacturer": db_equip.manufacturer}
        )

        self.db.commit()
        self.db.refresh(db_equip)
        return db_equip

    def get_equipment_templates(self, category: str, model_type: str):
        from services.equipment_template_service import EquipmentTemplateService

        templates = EquipmentTemplateService(self.db).get_compatible_parts(category, model_type)
        if templates:
            return templates
        return [{"part_name": "通用部件", "specification": ""}]

    def get_equipment_by_id(self, equipment_id: int):
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()

    def update_equipment(self, equipment_id: int, update_data, user_id: int):
        db_equip = self.get_equipment_by_id(equipment_id)
        if not db_equip:
            return None

        # 更新主字段
        fields = ['category', 'model_type', 'name', 'manufacturer', 'tonnage', 'span', 'lifting_height',
                  'work_class', 'installation_location', 'last_inspection_date',
                  'next_inspection_date', 'warranty_end_date', 'applied_template_id',
                  'applied_template_version', 'submit_as_template_candidate']
        for field in fields:
            val = getattr(update_data, field, None)
            if val is not None:
                setattr(db_equip, field, val)
        if update_data.inspection_items is not None:
            db_equip.inspection_items_json = json.dumps(update_data.inspection_items, ensure_ascii=False)

        # 更新部件清单（如果提供了 parts 则先删除再重建）
        if update_data.parts is not None:
            self.db.query(EquipmentPart).filter(EquipmentPart.equipment_id == equipment_id).delete()
            for part in update_data.parts:
                db_part = EquipmentPart(
                    equipment_id=equipment_id,
                    part_name=part.part_name,
                    specification=part.specification,
                    quantity=part.quantity
                )
                self.db.add(db_part)

        # 写入操作审计日志 - PRD 铁律：所有写操作必须记录
        write_audit_log(
            db=self.db,
            user_id=user_id,
            action="UPDATE",
            table_name="equipments",
            record_id=equipment_id,
            new_value={"name": db_equip.name, "category": db_equip.category, "manufacturer": db_equip.manufacturer}
        )

        self.db.commit()
        self.db.refresh(db_equip)
        return db_equip
