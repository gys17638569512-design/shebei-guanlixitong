import sqlite3

# 连接数据库
conn = sqlite3.connect('crane_mms.db')
cursor = conn.cursor()

# 检查 users 表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
table_exists = cursor.fetchone()

if table_exists:
    print("Users table exists")
    # 查询所有用户
    cursor.execute("SELECT id, username, name, role FROM users;")
    users = cursor.fetchall()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Name: {user[2]}, Role: {user[3]}")
else:
    print("Users table does not exist")

# 关闭连接
conn.close()