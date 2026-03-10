import sqlite3
import os

def seed_test_customer():
    db_path = "crane_mms.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 未找到数据库文件: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 强制更新结构
        columns = [
            ("login_phone", "VARCHAR(20)"),
            ("sms_code", "VARCHAR(6)"),
            ("sms_code_expires_at", "DATETIME")
        ]
        
        for col_name, col_type in columns:
            try:
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                print(f"✨ 字段 {col_name} 增加成功。")
            except sqlite3.OperationalError as e:
                # 如果字段已存在，sqlite 会报错 duplicate column name
                if "duplicate column name" in str(e):
                    pass
                else:
                    print(f"⚠️ 字段 {col_name} 处理异常: {e}")

        # 2. 设置测试数据
        test_phone = "13800138000"
        cursor.execute("SELECT id, company_name FROM customers LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            print("❌ 数据库中无客户记录，请先在 PC 管理后台创建一个客户后再运行此脚本。")
            return
            
        customer_id, company_name = row
        cursor.execute("UPDATE customers SET login_phone = ? WHERE id = ?", (test_phone, customer_id))
        conn.commit()
        
        print(f"✅ 测试客户 '{company_name}' 已成功绑定手机号: {test_phone}")
        print("-" * 30)
        print("🚀 现在可以测试客户门户登录了！")
        
        conn.close()
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    seed_test_customer()
