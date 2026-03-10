import requests

BASE_URL = "http://localhost:8001/api/v1"
ADMIN_CRED = {"username": "admin", "password": "123"}

def login(creds):
    res = requests.post(f"{BASE_URL}/auth/login/token", data=creds)
    return res.json()["access_token"]

def main():
    admin_token = login(ADMIN_CRED)
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. 查一下技术员
    users = requests.get(f"{BASE_URL}/system/users", headers=headers).json()["data"]
    tech = next((u for u in users if u["role"] == "TECH"), None)
    if not tech:
        print("未找到 TECH 用户")
        return
    
    tech_token = login({"username": tech["username"], "password": "123"})
    tech_headers = {"Authorization": f"Bearer {tech_token}"}
    
    # 2. 创建工单
    order_data = {
        "equipment_id": 1,
        "customer_id": 1,
        "technician_id": tech["id"],
        "order_type": "临时维保",
        "plan_date": "2024-05-01"
    }
    order = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers).json()["data"]
    order_id = order["id"]
    print(f"创建工单 {order_id}")
    
    # 3. 越级结单测试 (应当失败)
    res = requests.put(f"{BASE_URL}/orders/{order_id}/complete", json={
        "sign_url": "test",
        "inspection_items": []
    }, headers=tech_headers)
    print("越级结单拦截测试:", res.status_code, res.json())
    
    # 4. 正常打卡
    res = requests.put(f"{BASE_URL}/orders/{order_id}/checkin", json={
        "checkin_time": "2024-05-01T10:00:00",
        "checkin_address": "Test"
    }, headers=tech_headers)
    print("正常打卡测试:", res.status_code, res.json())
    
    # 5. 重复打卡测试 (应当失败)
    res = requests.put(f"{BASE_URL}/orders/{order_id}/checkin", json={
        "checkin_time": "2024-05-01T10:00:00",
        "checkin_address": "Test"
    }, headers=tech_headers)
    print("重复打卡拦截测试:", res.status_code, res.json())
    
    # 6. 未签名结单测试 (应当失败)
    res = requests.put(f"{BASE_URL}/orders/{order_id}/complete", json={
        "sign_url": "",
        "inspection_items": []
    }, headers=tech_headers)
    print("未签名结单拦截测试:", res.status_code, res.json())
    
    # 7. 正常结单测试
    res = requests.put(f"{BASE_URL}/orders/{order_id}/complete", json={
        "sign_url": "http://example.com/sign",
        "problem_description": "无异常",
        "solution": "常规保养",
        "inspection_items": []
    }, headers=tech_headers)
    print("正常结单测试:", res.status_code, res.json())

if __name__ == "__main__":
    main()
