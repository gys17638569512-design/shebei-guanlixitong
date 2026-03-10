from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from core.database import engine, Base

# 导入所有模型，确保它们被注册到 Base 中
from models.user import User
from models.customer import Customer
from models.equipment import Equipment
from models.work_order import WorkOrder, InspectionItem, WorkOrderPart
from models.audit_log import AuditLog
from models.part import Part
from models.repair_order import RepairOrder

# 创建数据库表
Base.metadata.create_all(bind=engine)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.exceptions import BusinessError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError
from core.response import err
from routers import auth, order, upload, report, user, customer, equipment, part, audit_log, stats
from routers import portal, repair
import uvicorn

description = """
<div align="center">
  <img src="/static/logo.png" width="120" style="margin-bottom: 20px; border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
  <h1>智能起重机维保管理系统 V1.0</h1>
  <p><i>基于工业互联网技术的特种设备全生命周期管理后端核心集群</i></p>
</div>

---

### 🚀 快速上手保姆级对接指南

#### 1. 身份认证 (获取专属钥匙)
本系统采用安全加密的 Bearer Token 鉴权机制。若要测试业务接口，请先点击下方的 **[认证模块]**：
- 调用 `POST /api/v1/auth/login` (账号: admin / 密码: 123)
- 在返回结果中找到 `access_token` 并**完整复制**其乱码内容。

#### 2. 全局授权 (激活测试环境)
- 点击页面右上角的绿色按钮 **Authorize 🔓**。
- 在弹窗的输入框内粘贴刚才复制的 Token。
- 点击 **Authorize** 确认，看到锁头闭合后关闭弹窗即可。

#### 3. 数据规范与响应码
- **业务载体**: 所有响应均封装在 `{"code": 200, "msg": "success", "data": {...}}` 中。
- **状态提示**: `200` 代表业务成功；`400` 代表业务逻辑拦截；`401/403` 代表权限缺失。

---
"""

tags_metadata = [
    {"name": "认证模块", "description": "系统的守门员：处理用户登录、身份验证和访问授权。"},
    {"name": "工单中心", "description": "系统的核心血脉：派单、打卡、实施数据采集及完工流水线。"},
    {"name": "客户管理", "description": "档案基石：维护全国各地的起重机使用客户信息。"},
    {"name": "设备档案", "description": "物理资产数字化：记录起重机型号、吨位、跨度及核心部件清单。"},
    {"name": "文件上传", "description": "云端文件与图片归档服务。"},
    {"name": "报告生成", "description": "维保结单后可触达客户的 PDF 维修报告单生成引擎。"},
    {"name": "安全审计", "description": "系统痕迹追踪：记录所有敏感数据的增删改记录。"},
    {"name": "统计中心", "description": "数据驾驶舱：聚合全业务线指标，透视运营效率。"}
]

app = FastAPI(
    title="智能起重机维保管理系统 API 接口平台",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None
)

# 挂载静态文件
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# 自定义 Swagger UI HTML (注入深海蓝主题 CSS)
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - 开发者控制台",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="/static/logo.png",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(BusinessError)
async def business_exception_handler(request, exc: BusinessError):
    return JSONResponse(status_code=400, content=err(400, exc.msg))

@app.exception_handler(UnauthorizedError)
async def unauthorized_exception_handler(request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content=err(401, exc.msg))

@app.exception_handler(ForbiddenError)
async def forbidden_exception_handler(request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content=err(403, exc.msg))

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc: NotFoundError):
    return JSONResponse(status_code=404, content=err(404, exc.msg))

@app.exception_handler(ConflictError)
async def conflict_exception_handler(request, exc: ConflictError):
    return JSONResponse(status_code=409, content=err(409, exc.msg))

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=err(exc.status_code, str(exc.detail)))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content=err(400, f"参数验证错误: {exc.errors()}"))

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(order.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(customer.router, prefix="/api/v1")
app.include_router(equipment.router, prefix="/api/v1")
app.include_router(part.router, prefix="/api/v1")
app.include_router(audit_log.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(portal.router, prefix="/api/v1")
app.include_router(repair.router, prefix="/api/v1")

@app.get("/", tags=["默认连接"], summary="查询服务根节点状态")
def read_root():
    return {"message": "欢迎抵达智能起重机维保管理系统后端接口集群节点！"}

@app.get("/health", tags=["默认连接"], summary="后端核心存活检测")
def health_check():
    return {"status": "healthy", "msg": "系统各心跳指标运行健康！"}