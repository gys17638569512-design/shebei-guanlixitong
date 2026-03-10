import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('crane-mms/backend/crane_mms.db')
cursor = conn.cursor()

# 查看所有表
print("数据库表结构：")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"\n表名: {table[0]}")
    # 查看表结构
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")

# 查看用户表数据
print("\n用户表数据：")
cursor.execute("SELECT id, username, name, role FROM users;")
users = cursor.fetchall()
for user in users:
    print(f"  - ID: {user[0]}, 用户名: {user[1]}, 姓名: {user[2]}, 角色: {user[3]}")

# 查看客户表数据
print("\n客户表数据：")
cursor.execute("SELECT id, company_name, contact_name, contact_phone FROM customers;")
customers = cursor.fetchall()
for customer in customers:
    print(f"  - ID: {customer[0]}, 公司名称: {customer[1]}, 联系人: {customer[2]}, 电话: {customer[3]}")

# 查看设备表数据
print("\n设备表数据：")
cursor.execute("SELECT id, name, model_type, customer_id FROM equipments;")
equipments = cursor.fetchall()
for equipment in equipments:
    print(f"  - ID: {equipment[0]}, 名称: {equipment[1]}, 型号: {equipment[2]}, 客户ID: {equipment[3]}")

# 关闭连接
conn.close()
