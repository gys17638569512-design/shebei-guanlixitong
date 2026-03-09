from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 测试登录接口
print("Testing login API with TestClient...")
response = client.post(
    "/api/v1/auth/login",
    json={"username": "admin", "password": "123"}
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# 测试根路径
print("\nTesting root path...")
root_response = client.get("/")
print(f"Status code: {root_response.status_code}")
print(f"Response: {root_response.json()}")