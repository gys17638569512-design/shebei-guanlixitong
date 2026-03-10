import requests
import sqlite3
import json

API_BASE = "http://localhost:8001/api/v1"

def check_res(res, label):
    if res.status_code >= 400:
        print(f"❌ {label} 失败 ({res.status_code}): {res.text}")
        return False
    try:
        res.json()
    except:
        print(f"❌ {label} 返回了非 JSON 数据: {res.text}")
        return False
    return True

def run_e2e_test():
    print("=== [E2E] 核心业务全链路验证 ===")
    
    # 1. 工程师登录 (tech01/123456)
    login_res = requests.post(f"{API_BASE}/auth/login", json={"username": "tech01", "password": "123456"})
    if not check_res(login_res, "工程师登录"): return
    tech_token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {tech_token}"}
    print("✅ 工程师登录成功")

    # 2. 获取任务并处理
    orders_res = requests.get(f"{API_BASE}/orders/my", headers=headers)
    if not check_res(orders_res, "获取任务列表"): return
    orders = orders_res.json()["data"]
    if not orders:
        print("⚠️ 该工程师暂无待处理工单")
        return

    # 找到一个可以操作的工单
    order = next((o for o in orders if o['status'] in ('PENDING', 'IN_PROGRESS', 'PENDING_SIGN')), orders[0])
    order_id = order['id']
    print(f"✅ 获取工单 #{order_id} (当前状态: {order['status']})")

    # 3. 现场签到
    if order['status'] == 'PENDING':
        checkin_res = requests.put(
            f"{API_BASE}/orders/{order_id}/checkin", 
            headers=headers,
            json={"checkin_address": "测试工地 A 区", "checkin_time": "2024-03-10T10:00:00Z"}
        )
        if not check_res(checkin_res, "工程师签到"): return
        print(f"✅ 工程师签到成功")

    # 4. 推送客户签字
    # 如果已经是 IN_PROGRESS 或者刚签到完
    push_res = requests.put(
        f"{API_BASE}/orders/{order_id}/push_sign",
        headers=headers,
        json={
            "problem_description": "起重机钢丝绳轻微磨损",
            "solution": "已润滑并建议下月更换",
            "photo_urls": ["http://test.com/photo.jpg"]
        }
    )
    if not check_res(push_res, "工程师推送签字"): return
    print(f"✅ 工程师推送签字成功")

    # 5. 客户门户登录
    # 自动获取验证码
    conn = sqlite3.connect("crane_mms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sms_code FROM customers WHERE login_phone='13800138000'")
    row = cursor.fetchone()
    code = row[0]
    conn.close()

    if not code:
        print("❌ 数据库中未找到验证码，请确保已触发 send_code")
        return

    portal_login_res = requests.post(f"{API_BASE}/portal/auth/login", json={
        "phone": "13800138000",
        "code": code
    })
    if not check_res(portal_login_res, "客户门户登录"): return
    portal_token = portal_login_res.json()["data"]["access_token"]
    portal_headers = {"Authorization": f"Bearer {portal_token}"}
    print("✅ 客户门户登录成功")

    # 6. 客户签字完成工单
    sign_res = requests.post(
        f"{API_BASE}/portal/orders/{order_id}/sign",
        headers=portal_headers,
        json={"sign_url": "data:image/png;base64,xxxxTESTSIGNBAR"}
    )
    if not check_res(sign_res, "客户签字结单"): return
    print(f"✅ 客户签字结单成功 (工单已完工)")

if __name__ == "__main__":
    run_e2e_test()
