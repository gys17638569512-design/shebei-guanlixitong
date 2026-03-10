import sqlite3
import os
import requests
import json
from datetime import datetime

DB_PATH = "crane_mms.db"
API_BASE = "http://localhost:8001/api/v1"

def check_db():
    print("=== [1] 数据库完整性检查 ===")
    if not os.path.exists(DB_PATH):
        print(f"❌ 找不到数据库文件: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查核心表
    required_tables = ['users', 'customers', 'equipments', 'work_orders', 'parts', 'audit_logs']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [t[0] for t in cursor.fetchall()]
    
    for table in required_tables:
        if table in existing_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ 表 [{table}] 正常, 记录记录数: {count}")
        else:
            print(f"❌ 缺失表: {table}")

    # 检查二期新增字段
    cursor.execute("PRAGMA table_info(customers)")
    cols = [c[1] for c in cursor.fetchall()]
    new_cols = ['login_phone', 'sms_code']
    for col in new_cols:
        if col in cols:
            print(f"✅ 客户表字段 [{col}] 存在")
        else:
            print(f"❌ 客户表缺失字段: {col}")
    
    conn.close()
    return True

def check_api_health():
    print("\n=== [2] 后端 API 健康检查 ===")
    try:
        # 测试不带 Token 的 401
        res = requests.get(f"{API_BASE}/equipments")
        if res.status_code == 401:
            print("✅ 鉴权控制正常 (401 Unauthorized)")
        
        # 测试门户登录接口 (Mock)
        # 先确保有一个测试手机号
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE customers SET login_phone = '13800138000' WHERE id = (SELECT id FROM customers LIMIT 1)")
        conn.commit()
        conn.close()
        
        # 1. 请求验证码
        res = requests.post(f"{API_BASE}/portal/auth/send_code", json={"phone": "13800138000"})
        print(f"✅ 发送验证码 API: {res.status_code} {res.json().get('msg')}")
        
    except Exception as e:
        print(f"❌ API 测试连接失败: {e}")

if __name__ == "__main__":
    check_db()
    check_api_health()
