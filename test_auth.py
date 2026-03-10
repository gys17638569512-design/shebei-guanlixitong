import requests

# 测试不同用户登录
def test_login(username, password):
    print(f"\n测试用户登录: {username}")
    try:
        response = requests.post("http://localhost:8001/api/v1/auth/login", json={
            "username": username,
            "password": password
        })
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"访问令牌: {data['data']['access_token'][:50]}...")
            print(f"用户信息: {data['data']['user']}")
            return data['data']['access_token']
        else:
            print(f"错误: {response.json()}")
            return None
    except Exception as e:
        print(f"错误: {e}")
        return None

# 测试使用token访问受保护的接口
def test_protected_endpoint(token):
    print("\n测试访问受保护的接口")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        # 测试获取用户列表
        response = requests.get("http://localhost:8001/api/v1/users", headers=headers)
        print(f"获取用户列表 - 状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"用户列表: {response.json()}")
        else:
            print(f"错误: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")

# 测试无效token
def test_invalid_token():
    print("\n测试无效token")
    headers = {
        "Authorization": "Bearer invalid_token"
    }
    try:
        response = requests.get("http://localhost:8001/api/v1/users", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")

# 运行测试
if __name__ == "__main__":
    # 测试管理员登录
    admin_token = test_login("admin", "123")
    if admin_token:
        test_protected_endpoint(admin_token)
    
    # 测试经理登录
    manager_token = test_login("manager01", "123")
    if manager_token:
        test_protected_endpoint(manager_token)
    
    # 测试工程师登录
    tech_token = test_login("tech01", "123")
    if tech_token:
        test_protected_endpoint(tech_token)
    
    # 测试无效token
    test_invalid_token()
