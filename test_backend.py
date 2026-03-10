import requests

# 测试根路径
print("测试根路径 /")
try:
    response = requests.get("http://localhost:8001/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试健康检查接口 /health")
try:
    response = requests.get("http://localhost:8001/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试登录接口 /api/v1/auth/login")
try:
    response = requests.post("http://localhost:8001/api/v1/auth/login", json={
        "username": "admin",
        "password": "123"
    })
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")
