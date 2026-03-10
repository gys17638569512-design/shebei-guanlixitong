import os
import sys
from sqlalchemy.orm import Session
from core.database import engine, SessionLocal, Base
from models.user import User, RoleEnum
from models.customer import Customer, Contact
from models.equipment import Equipment, EquipmentPart
from models.work_order import WorkOrder, OrderStatus


def init_db():
    # 创建数据库表
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        from core.security import get_password_hash
        
        # 创建用户 - 使用 bcrypt 哈希密码
        admin = User(
            username="admin",
            password_hash=get_password_hash("Admin@2024"),
            role=RoleEnum.ADMIN,
            name="管理员",
            phone="13800000001"
        )
        manager01 = User(
            username="manager01",
            password_hash=get_password_hash("Manager@2024"),
            role=RoleEnum.MANAGER,
            name="经理",
            phone="13800000002"
        )
        db.add_all([admin, manager01])
        db.commit()
        db.refresh(manager01)

        tech01 = User(
            username="tech01",
            password_hash=get_password_hash("Tech@2024"),
            role=RoleEnum.TECH,
            name="工程师",
            phone="13800000003",
            manager_id=manager01.id
        )
        db.add(tech01)
        db.commit()
        db.refresh(tech01)
        
        # 创建客户
        customer = Customer(
            company_name="测试公司",
            contact_name="张三",
            contact_phone="13800138000",
            login_phone="13800138000",
            address="北京市朝阳区"
        )
        db.add(customer)
        db.commit()
        
        # 创建设备
        equipment = Equipment(
            customer_id=customer.id,
            name="桥式起重机",
            model_type="QD型",
            category="桥式起重机",
            tonnage="10吨",
            span="16米",
            lifting_height="8米",
            work_class="A5",
            installation_location="车间1"
        )
        db.add(equipment)
        db.commit()
        
        # 创建设备部件
        parts = [
            EquipmentPart(
                equipment_id=equipment.id,
                part_name="吊钩",
                specification="10吨",
                quantity=1
            ),
            EquipmentPart(
                equipment_id=equipment.id,
                part_name="钢丝绳",
                specification="Φ12mm",
                quantity=1
            )
        ]
        db.add_all(parts)
        db.commit()
        
        # 创建工单
        from datetime import date
        work_order = WorkOrder(
            customer_id=customer.id,
            equipment_id=equipment.id,
            technician_id=tech01.id,  # tech01
            plan_date=date(2026, 3, 10),
            status=OrderStatus.PENDING
        )
        db.add(work_order)
        db.commit()
        
        # 6. 创建初始检查模板
        import json
        from models.check_template import CheckTemplate
        items = [
            {"name": "主梁", "required": True, "order": 1},
            {"name": "端梁", "required": True, "order": 2},
            {"name": "大车运行机构", "required": True, "order": 3},
            {"name": "小车运行机构", "required": True, "order": 4},
            {"name": "起升机构", "required": True, "order": 5},
            {"name": "制动器", "required": True, "order": 6},
            {"name": "限位开关", "required": True, "order": 7},
            {"name": "钢丝绳", "required": True, "order": 8}
        ]
        template = CheckTemplate(
            name="桥式起重机月检标准模板",
            category="桥式起重机",
            version=1,
            items=json.dumps(items, ensure_ascii=False),
            is_active=True,
            created_by=admin.id
        )
        db.add(template)
        db.commit()
        
        print("测试数据初始化完成！")
        print("登录账号：")
        print("  管理员：admin     / Admin@2024")
        print("  经理：  manager01 / Manager@2024")
        print("  工程师：tech01    / Tech@2024")
        
    except Exception as e:
        print(f"初始化失败：{e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()