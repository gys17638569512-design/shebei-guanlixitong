import requests
import json

# 测试登录接口
url = "http://localhost:8000/api/v1/auth/login"
headers = {"Content-Type": "application/json"}
data = {
    "username": "admin",
    "password": "admin123"
}

print("Testing login API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data)}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code != 200:
        print("Login failed!")
    else:
        print("Login successful!")
except Exception as e:
    print(f"Error: {e}")