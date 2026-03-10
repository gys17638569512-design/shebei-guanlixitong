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

# 测试客户CRUD
def test_customer_crud(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试客户CRUD ===")
    
    # 1. 获取客户列表
    print("1. 获取客户列表")
    response = requests.get("http://localhost:8001/api/v1/customers", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 创建新客户
    print("\n2. 创建新客户")
    new_customer = {
        "company_name": "测试客户",
        "contact_name": "李四",
        "contact_phone": "13900139000",
        "address": "北京市朝阳区"
    }
    response = requests.post("http://localhost:8001/api/v1/customers", json=new_customer, headers=headers)
    print(f"状态码: {response.status_code}")
    customer_data = response.json()
    print(f"响应: {customer_data}")
    customer_id = customer_data['data']['id'] if response.status_code == 200 else None
    
    # 3. 获取客户详情
    if customer_id:
        print(f"\n3. 获取客户详情 (ID: {customer_id})")
        response = requests.get(f"http://localhost:8001/api/v1/customers/{customer_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 4. 更新客户信息
    if customer_id:
        print(f"\n4. 更新客户信息 (ID: {customer_id})")
        updated_customer = {
            "company_name": "更新后的测试客户",
            "contact_name": "李四更新",
            "contact_phone": "13900139001",
            "address": "北京市海淀区"
        }
        response = requests.put(f"http://localhost:8001/api/v1/customers/{customer_id}", json=updated_customer, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 5. 删除客户
    if customer_id:
        print(f"\n5. 删除客户 (ID: {customer_id})")
        response = requests.delete(f"http://localhost:8001/api/v1/customers/{customer_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

# 测试设备CRUD
def test_equipment_crud(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试设备CRUD ===")
    
    # 1. 获取设备列表
    print("1. 获取设备列表")
    response = requests.get("http://localhost:8001/api/v1/equipments", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 2. 创建新设备
    print("\n2. 创建新设备")
    new_equipment = {
        "customer_id": 1,
        "name": "测试设备",
        "model_type": "QD型",
        "category": "桥式起重机",
        "tonnage": "10吨",
        "span": "20米",
        "lifting_height": "10米",
        "work_class": "A5",
        "installation_location": "工厂车间"
    }
    response = requests.post("http://localhost:8001/api/v1/equipments", json=new_equipment, headers=headers)
    print(f"状态码: {response.status_code}")
    equipment_data = response.json()
    print(f"响应: {equipment_data}")
    equipment_id = equipment_data['data']['id'] if response.status_code == 200 else None
    
    # 3. 获取设备详情
    if equipment_id:
        print(f"\n3. 获取设备详情 (ID: {equipment_id})")
        response = requests.get(f"http://localhost:8001/api/v1/equipments/{equipment_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 4. 更新设备信息
    if equipment_id:
        print(f"\n4. 更新设备信息 (ID: {equipment_id})")
        updated_equipment = {
            "name": "更新后的测试设备",
            "model_type": "QD型",
            "category": "桥式起重机",
            "tonnage": "15吨",
            "span": "25米",
            "lifting_height": "12米",
            "work_class": "A6",
            "installation_location": "新工厂车间"
        }
        response = requests.put(f"http://localhost:8001/api/v1/equipments/{equipment_id}", json=updated_equipment, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    
    # 5. 删除设备
    if equipment_id:
        print(f"\n5. 删除设备 (ID: {equipment_id})")
        response = requests.delete(f"http://localhost:8001/api/v1/equipments/{equipment_id}", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")

# 运行测试
if __name__ == "__main__":
    token = get_admin_token()
    if token:
        test_customer_crud(token)
        test_equipment_crud(token)
