import sys
import os

# 将 backend 目录加入路径以导入模型 (修正路径到 crane-mms/backend)
backend_path = os.path.join(os.getcwd(), "crane-mms", "backend")
sys.path.append(backend_path)

from core.database import SessionLocal
from models.customer import Customer

def seed_test_customer():
    db = SessionLocal()
    try:
        # 查找一个客户
        customer = db.query(Customer).first()
        if not customer:
            print("❌ 数据库中无客户记录，请先通过 PC 后端创建一个客户。")
            return
        
        test_phone = "13800138000"
        customer.login_phone = test_phone
        db.commit()
        
        print(f"✅ 测试客户已就绪！")
        print(f"公司名称: {customer.company_name}")
        print(f"测试登录手机号: {test_phone}")
        print("-" * 30)
        print("测试流程建议：")
        print(f"1. 访问 http://localhost:3001/login")
        print(f"2. 输入手机号 {test_phone}")
        print(f"3. 点击获取验证码，并查看后端终端日志输出的 6 位数字汇集成。")
        print(f"4. 输入验证码完成登录。")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_customer()
