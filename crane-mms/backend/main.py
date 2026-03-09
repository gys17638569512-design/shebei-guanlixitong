from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base

# 导入所有模型，确保它们被注册到 Base 中
from models.user import User
from models.customer import Customer
from models.equipment import Equipment
from models.work_order import WorkOrder, InspectionItem
from models.audit_log import AuditLog

# 创建数据库表
Base.metadata.create_all(bind=engine)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.exceptions import BusinessError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError
from core.response import err
from routers import auth, order, upload, report, user, customer, equipment

description = """
欢迎使用 **智能起重机维保管理系统** 的后台接口文档测试平台！此界面可供前端开发、移动端对接、以及第三方系统接入测试使用。

### 📖 快速保姆级使用指南 (新手必读)

#### 第一步：登录与身份认证 (获取专属 Token)
系统内所有的业务接口（工单、设备等）都需要验证您的身份权限。如果您是第一次打开本页面，请先获取一把“钥匙”：
1. 往下滚动，展开粗体的 **【认证模块】** 列表，找到第一项 `POST /api/v1/auth/login` (用户登录) 接口。
2. 点击右侧出现的 **[ Try it out ]** (开始尝试执行) 按钮，以激活参数输入框。
3. 在请求体的输入框 (`Request body`) 中，填入测试用的账号密码代码块（预留管理员测试账户 `username`: "admin"，`password`: "123"）。
4. 点击下方蓝色的大按钮 **[ Execute ]** (执行请求)。
5. 等待请求转圈完成后，系统会在下方的 `Responses` (响应体) 中返回给您一串成功信息。请在其中**仔细复制**名为 `access_token` 后边的那一长串乱码字符（**注意：千万不要复制双引号**）。

#### 第二步：配置全局鉴权锁 (插入并激活您的“钥匙”)
1. 滚动回到本页面的最上方，在右侧靠上的位置有一个醒目的带锁图标绿色按钮：**[ Authorize ]** (点击授权)。
2. 点击弹出一个身份验证窗口后，在 `Value` (令牌值) 的输入框内，**粘贴**您刚才辛辛苦苦复制出来的那一长串 `access_token` 字符串。
3. 粘贴完毕后，点击右侧的 **Authorize** (授权) 按钮。如果成功，系统会将锁的图标锁定起来变成“闭合状态🔐”。
4. 点击 **Close** 关闭这个弹窗即可。
5. 🎉 **大功告成！** 现在系统记录了您的操作者身份。您可以大胆地向下翻阅并测试任何包含业务权限判断的【工单中心】、【文件报告】接口了。系统会自动带着您的身份证明去请求后台服务！

#### 第三步：业务接口测试与响应格式
- 所有业务接口均符合标准的 JSON 装包结构：`{"code": 状态码, "msg": "请求描述信息", "data": 请求到的数据负载}`。
- 当 `code` 等于 `200` 代表业务逻辑成功，其它状态码如 `400`、`403`、`404` 代表有明确的错误和拦截发生（对应的 `msg` 中都有详细的中文报错原因解释），可以直接截图提 Bug 给开发团队。

---
"""

tags_metadata = [
    {
        "name": "认证模块",
        "description": "系统的守门员：处理用户登录、身份验证和签发访问授权短令牌。",
    },
    {
        "name": "工单中心",
        "description": "系统的核心血脉：获取派发给我的任务、现场实施定位打卡、上传检查项数据以及结束提交维修工单。",
    },
    {
        "name": "文件上传",
        "description": "系统的云端储藏室：承载前端传来的现场故障环境图片、设备图片、以及客户签署处理完成的电子签绘板签名图片落库与缩略图存储工作。",
    },
    {
        "name": "报告生成",
        "description": "系统的信息集大成者：将工单所有的信息汇聚一处，结合客户电子签名进行签署并导出为可以发送给客户或归档的不可篡改的电子版 PDF 维修单。",
    },
    {
        "name": "默认连接",
        "description": "系统的基础心跳检测接口。",
    }
]

app = FastAPI(
    title="智能起重机维保管理系统 API 接口平台",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
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


@app.get("/", tags=["默认连接"], summary="查询服务访问根节点状态")
def read_root():
    return {"message": "欢迎抵达智能起重机维保管理系统后端接口集群节点！接口通信就绪。"}


@app.get("/health", tags=["默认连接"], summary="后端核心存活与负载健康检测")
def health_check():
    return {"status": "healthy", "msg": "系统各项心跳指标运行健康！"}