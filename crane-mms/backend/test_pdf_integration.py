import requests
import time
import os

BASE_URL = "http://localhost:8001/api/v1"

def login(username, password):
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    if res.status_code != 200:
        print("Login failed:", res.text)
        return None
    return res.json()["data"]["access_token"]

def wait_for_pdf(order_id, headers):
    for i in range(10):
        time.sleep(1)
        res = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers).json()
        pdf_url = res["data"].get("pdf_report_url")
        if pdf_url:
            print(f"✅ 成功! 提取到 PDF URL: {pdf_url}")
            return pdf_url
    print("❌ 失败! 10秒内未生成 PDF")
    return None

def main():
    admin_token = login("admin", "123")
    if not admin_token: return
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    users_data = requests.get(f"{BASE_URL}/users", headers=headers).json().get("data", [])
    if isinstance(users_data, dict) and "items" in users_data:
        users = users_data["items"]
    else:
        users = users_data
        
    tech = next((u for u in users if u["role"] == "TECH" or u.get("role") == "TECH"), None)
    if not tech:
        print("未找到测试用 TECH 账号")
        return
    
    tech_token = login(tech["username"], "123")
    tech_headers = {"Authorization": f"Bearer {tech_token}"}
    
    print("1. Admin 发起工单...")
    order = requests.post(f"{BASE_URL}/orders", json={
        "equipment_id": 1, "customer_id": 1, "technician_id": tech["id"], 
        "order_type": "特级巡检", "plan_date": "2024-06-01"
    }, headers=headers).json()["data"]
    order_id = order["id"]
    
    print("2. Tech 现场打卡...")
    res2 = requests.put(f"{BASE_URL}/orders/{order_id}/checkin", json={
        "checkin_time": "2024-06-01T10:00:00", "checkin_address": "厂区车间 A"
    }, headers=tech_headers)
    print("Checkin Response:", res2.status_code, res2.text)
    
    print("3. Tech 签署并结单，触发后台 PDF 构建流水线...")
    res3 = requests.put(f"{BASE_URL}/orders/{order_id}/complete", json={
        "sign_url": "https://via.placeholder.com/300x150.png?text=Signed",
        "problem_description": "起重机运行测试无异常，制动器正常。",
        "solution": "已注入高级润滑脂，清理各部粉尘。",
        "inspection_items": [
            {"item_name": "联轴器排查", "result": "NORMAL", "comment": "无裂纹"},
            {"item_name": "电气柜绝缘", "result": "NORMAL", "comment": "绝缘达标"}
        ]
    }, headers=tech_headers)
    print("Complete Response:", res3.status_code, res3.text)
    
    print("4. 轮询侦测异步挂载结果...")
    wait_for_pdf(order_id, headers)

if __name__ == "__main__":
    main()
