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
            tonnage=equip_data.tonnage,
            span=equip_data.span,
            lifting_height=equip_data.lifting_height,
            work_class=equip_data.work_class,
            installation_location=equip_data.installation_location,
            last_inspection_date=equip_data.last_inspection_date,
            next_inspection_date=equip_data.next_inspection_date,
            warranty_end_date=equip_data.warranty_end_date
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
            new_value={"name": db_equip.name, "customer_id": db_equip.customer_id, "category": db_equip.category}
        )

        self.db.commit()
        self.db.refresh(db_equip)
        return db_equip

    def get_equipment_templates(self, category: str, model_type: str):
        # 这是一个模拟的方法，因为 PRD 中提到未来可能由字典表维护
        # 这里为了满足前端的联动查询，返回硬编码的常见模版
        templates = {
            "桥式起重机": [
                {"part_name": "主梁", "specification": "Q235B"},
                {"part_name": "端梁", "specification": ""},
                {"part_name": "起升机构", "specification": "含电动机、减速器、卷筒"},
                {"part_name": "小车运行机构", "specification": ""},
                {"part_name": "大车运行机构", "specification": ""},
                {"part_name": "电气控制箱", "specification": "变频控制"},
                {"part_name": "驾驶室", "specification": "联动台操作"},
                {"part_name": "吊钩组", "specification": "单钩"},
                {"part_name": "钢丝绳", "specification": "线接触型"},
            ],
            "门式起重机": [
                {"part_name": "主梁", "specification": "箱型"},
                {"part_name": "支腿", "specification": "L型或C型"},
                {"part_name": "地梁", "specification": ""},
                {"part_name": "起升机构", "specification": ""},
                {"part_name": "运行机构", "specification": ""}
            ],
            "悬臂起重机": [
                {"part_name": "立柱", "specification": "无缝钢管"},
                {"part_name": "回转臂", "specification": "工字钢"},
                {"part_name": "电动环链葫芦", "specification": ""},
                {"part_name": "滑触线", "specification": "C型轨"}
            ]
        }
        return templates.get(category, [{"part_name": "通用部件", "specification": ""}])

    def get_equipment_by_id(self, equipment_id: int):
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()

    def update_equipment(self, equipment_id: int, update_data, user_id: int):
        db_equip = self.get_equipment_by_id(equipment_id)
        if not db_equip:
            return None

        # 更新主字段
        fields = ['category', 'model_type', 'name', 'tonnage', 'span', 'lifting_height',
                  'work_class', 'installation_location', 'last_inspection_date',
                  'next_inspection_date', 'warranty_end_date']
        for field in fields:
            val = getattr(update_data, field, None)
            if val is not None:
                setattr(db_equip, field, val)

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
            new_value={"name": db_equip.name, "category": db_equip.category}
        )

        self.db.commit()
        self.db.refresh(db_equip)
        return db_equip
