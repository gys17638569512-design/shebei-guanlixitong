from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from routers import auth, order, upload, report

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="数字化起重机维修维保系统",
    description="数字化起重机维修维保系统 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(order.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "数字化起重机维修维保系统 API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 打印所有路由
print("=== Available Routes ===")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"{route.path} - {list(route.methods) if hasattr(route, 'methods') else 'GET'}")
