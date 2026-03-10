import requests

# 首先获取管理员token
def get_admin_token():
    response = requests.post("http://localhost:8001/api/v1/auth/login", json={
        "username": "admin",
        "password": "123"
    })
    if response.status_code == 200:
        return response.json()['data']['access_token']
    else:
        print("获取管理员token失败")
        return None

# 测试工单API
def test_orders_api(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试工单API ===")
    
    # 1. 获取工单列表
    print("1. 获取工单列表")
    response = requests.get("http://localhost:8001/api/v1/orders", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 创建新工单
    print("\n2. 创建新工单")
    new_order = {
        "customer_id": 1,
        "equipment_id": 1,
        "technician_id": 3,
        "plan_date": "2024-12-01",
        "order_type": "维保",
        "problem_description": "设备异响"
    }
    response = requests.post("http://localhost:8001/api/v1/orders", json=new_order, headers=headers)
    print(f"状态码: {response.status_code}")
    order_data = response.json()
    print(f"响应: {order_data}")
    order_id = order_data['data']['id'] if response.status_code == 200 else None
    
    # 3. 获取工单详情
    if order_id:
        print(f"\n3. 获取工单详情 (ID: {order_id})")
        response = requests.get(f"http://localhost:8001/api/v1/orders/{order_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 4. 更新工单状态
    if order_id:
        print(f"\n4. 更新工单状态 (ID: {order_id})")
        update_data = {
            "status": "IN_PROGRESS",
            "checkin_time": "2024-12-01T09:00:00",
            "checkin_address": "客户现场"
        }
        response = requests.put(f"http://localhost:8001/api/v1/orders/{order_id}", json=update_data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 5. 完成工单
    if order_id:
        print(f"\n5. 完成工单 (ID: {order_id})")
        complete_data = {
            "status": "COMPLETED",
            "solution": "更换磨损部件",
            "photo_urls": "[]"
        }
        response = requests.put(f"http://localhost:8001/api/v1/orders/{order_id}", json=complete_data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

# 运行测试
if __name__ == "__main__":
    token = get_admin_token()
    if token:
        test_orders_api(token)
