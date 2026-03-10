import logging
import traceback
import sys
import os

# 确保能导入项目模块
sys.path.append(os.getcwd())

from core.database import SessionLocal
from models.user import User
from services.order_service import push_for_sign

logging.basicConfig(level=logging.INFO)

def run_debug():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == 'tech01').first()
        if not user:
            print("❌ User tech01 not found")
            return
            
        print(f"Testing with User ID: {user.id}")
        
        # 尝试调用服务
        result = push_for_sign(
            db, 
            4, 
            {
                "problem_description": "debug test",
                "solution": "debug solution",
                "photo_urls": ["http://test.com/1.jpg"]
            }, 
            user
        )
        print(f"✅ Success: {result}")
        
    except Exception as e:
        print("❌ Caught Exception:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_debug()
