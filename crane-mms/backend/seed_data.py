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
        users = [
            User(
                username="admin",
                password_hash=get_password_hash("123"),
                role=RoleEnum.ADMIN,
                name="管理员"
            ),
            User(
                username="manager01",
                password_hash=get_password_hash("123"),
                role=RoleEnum.MANAGER,
                name="经理"
            ),
            User(
                username="tech01",
                password_hash=get_password_hash("123"),
                role=RoleEnum.TECH,
                name="工程师"
            )
        ]
        db.add_all(users)
        db.commit()
        
        # 创建客户
        customer = Customer(
            company_name="测试公司",
            contact_name="张三",
            contact_phone="13800138000",
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
            technician_id=3,  # tech01
            plan_date=date(2026, 3, 10),
            status=OrderStatus.PENDING
        )
        db.add(work_order)
        db.commit()
        
        print("测试数据初始化完成！")
        print("登录账号：")
        print("  管理员：admin     / 123")
        print("  经理：  manager01 / 123")
        print("  工程师：tech01    / 123")
        
    except Exception as e:
        print(f"初始化失败：{e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()