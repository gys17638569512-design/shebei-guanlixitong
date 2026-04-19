# 🛠️ 代码修复指令 — 智能起重机维保管理系统

> 将本文件完整粘贴给 Cursor AI，让它按顺序逐条修复。
> 每完成一条，运行 `pytest tests/ -v` 确认无回归后再执行下一条。

---

## 前置说明

**项目路径**：`crane-mms/backend/`
**当前问题**：代码审查发现 3 个严重问题 + 5 个重要问题，需按优先级依次修复。
**原则**：每次只改一个问题，改完立刻测试，不要批量修改后一起测。

---

## 🔴 严重问题（必须今天修复）

---

### FIX-01：密码强度不足

**文件**：`backend/seed_data.py`
**现状**：所有测试账号密码均为 `"123"`，安全风险极高。

**修改要求**：
将 seed_data.py 中所有账号密码改为以下强密码：

| 账号 | 新密码 |
|------|--------|
| admin | `Admin@2024` |
| manager01 | `Manager@2024` |
| tech01 | `Tech@2024` |

同时检查并更新以下位置的密码说明：
- `backend/seed_data.py` 底部的 print 输出
- `crane-mms/项目搭建记录.md` 中的账号密码说明
- 仓库根目录 `README.md`（如有密码说明）

**验证**：重新运行 `python seed_data.py`，然后用新密码登录 POST /api/v1/auth/login 确认成功。

---

### FIX-02：JWT Token 有效期过短

**文件**：`backend/core/settings.py`
**现状**：`ACCESS_TOKEN_EXPIRE_MINUTES = 30`，工程师现场作业会频繁掉线。

**修改要求**：
```python
# 修改前
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# 修改后
ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时，满足现场长时间作业需求
```

**验证**：登录后解码 JWT payload，确认 `exp` 字段为当前时间 + 24 小时。

---

### FIX-03：数据库连接池缺少保护配置

**文件**：`backend/core/database.py`
**现状**：`create_engine(settings.DATABASE_URL)` 无任何连接池参数，长时间运行后 MySQL 会主动断开连接导致 500 错误。

**修改要求**：
```python
# 修改前
engine = create_engine(settings.DATABASE_URL)

# 修改后
from sqlalchemy import create_engine

def _make_engine(url: str):
    # SQLite 用于测试，不需要连接池配置
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    # MySQL 生产配置
    return create_engine(
        url,
        pool_pre_ping=True,      # 每次使用前检测连接是否存活
        pool_size=10,            # 连接池大小
        max_overflow=20,         # 超出 pool_size 后最多额外创建数量
        pool_recycle=3600,       # 连接存活 1 小时后强制回收，防止 MySQL 超时断开
        pool_timeout=30,         # 等待连接超时时间（秒）
    )

engine = _make_engine(settings.DATABASE_URL)
```

**验证**：启动服务，等待 5 秒，调用任意接口，确认返回正常。

---

## 🟠 重要问题（本周内修复）

---

### FIX-04：User 模型缺少 phone 和 manager_id 字段

**文件**：`backend/models/user.py`
**现状**：User 表只有 5 个字段，缺少手机号（短信通知用）和 manager_id（数据隔离用）。

**修改要求**：

1. **修改 `backend/models/user.py`**，在 `name` 字段后添加：
```python
phone = Column(String(20), nullable=True, comment="手机号，用于短信通知")
manager_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="所属经理ID，TECH角色必填")
```

2. **修改 `backend/schemas/user.py`**，在用户相关 Schema 中补充这两个字段（可选字段，Optional[str]）。

3. **修改 `backend/seed_data.py`**，为测试账号添加 phone 数据：
```python
# admin: phone="13800000001"
# manager01: phone="13800000002"
# tech01: phone="13800000003", manager_id=manager01.id
```

**验证**：重新运行 `python seed_data.py`，调用 GET /api/v1/auth/me 确认返回数据包含 phone 字段。

---

### FIX-05：MANAGER 角色客户列表缺少数据隔离

**文件**：`backend/services/customer_service.py`
**现状**：任何角色调用 GET /customers 都能看到全部客户，MANAGER 应只能看到自己负责的客户。

**修改要求**：

修改 `CustomerService.get_customer_list()` 方法，增加 `current_user` 参数并按角色过滤：

```python
def get_customer_list(self, search: str = None, current_user=None):
    query = self.db.query(Customer)
    
    # MANAGER 只能看自己负责的客户（通过工单关联判断，或直接用 manager_id 字段）
    if current_user and current_user.role == "MANAGER":
        # 通过已有工单关联找到该经理相关的客户ID
        from models.work_order import WorkOrder
        managed_customer_ids = self.db.query(WorkOrder.customer_id).filter(
            WorkOrder.technician_id.in_(
                self.db.query(User.id).filter(User.manager_id == current_user.id)
            )
        ).distinct().all()
        customer_ids = [cid for (cid,) in managed_customer_ids]
        if customer_ids:
            query = query.filter(Customer.id.in_(customer_ids))
        else:
            return []  # 该经理名下暂无客户
    
    if search:
        query = query.filter(
            (Customer.company_name.contains(search)) |
            (Customer.contact_name.contains(search))
        )
    
    return query.all()
```

同时修改 `backend/routers/customer.py` 的 `get_customers` 接口，将 `current_user` 传入 service：
```python
customers = service.get_customer_list(search, current_user)
```

**验证**：用 manager01 Token 调用 GET /customers，确认只返回其名下数据；用 admin Token 调用确认返回全部数据。

---

### FIX-06：工单列表 N+1 查询问题（Router 层直接写 SQL）

**文件**：`backend/routers/order.py` 中的 `get_orders()` 函数（约第 158~195 行）
**现状**：工单列表接口在 for 循环内对每条工单各执行 3 次额外查询（查客户名、设备名、工程师名），100 条工单 = 301 次查询，严重影响性能。

**修改要求**：

1. **新建 `backend/repositories/work_order_repo.py`**（如不存在则创建，如已存在则在末尾追加），添加以下函数：

```python
from sqlalchemy.orm import Session, joinedload
from models.work_order import WorkOrder

def get_orders_with_relations(db: Session, status=None, technician_id=None, customer_id=None):
    """
    使用 joinedload 一次性加载工单及关联的客户、设备、工程师数据，避免 N+1 查询。
    """
    query = db.query(WorkOrder).options(
        joinedload(WorkOrder.customer),
        joinedload(WorkOrder.equipment),
        joinedload(WorkOrder.technician),
    )
    if status:
        query = query.filter(WorkOrder.status == status)
    if technician_id:
        query = query.filter(WorkOrder.technician_id == technician_id)
    if customer_id:
        query = query.filter(WorkOrder.customer_id == customer_id)
    
    return query.order_by(WorkOrder.created_at.desc()).all()
```

2. **修改 `backend/routers/order.py`** 的 `get_orders()` 函数，替换原有的循环查询：

```python
@router.get("", summary="获取所有工单（管理员/经理视图）")
async def get_orders(
    status: Optional[str] = Query(None),
    technician_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    from repositories.work_order_repo import get_orders_with_relations
    orders = get_orders_with_relations(db, status, technician_id, customer_id)
    
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_type": o.order_type,
            "status": o.status.value if hasattr(o.status, 'value') else o.status,
            "plan_date": str(o.plan_date),
            "created_at": str(o.created_at),
            "customer_id": o.customer_id,
            "customer_name": o.customer.company_name if o.customer else "—",
            "equipment_id": o.equipment_id,
            "equipment_name": o.equipment.name if o.equipment else "—",
            "technician_id": o.technician_id,
            "technician_name": o.technician.name if o.technician else "—",
        })
    return ok(data=result)
```

**验证**：调用 GET /orders，检查返回数据结构不变，且服务端日志中 SQL 查询次数从 3N+1 减少到 1 次。

---

### FIX-07：补充检查模板版本管理

**现状**：检查项 InspectionItem 直接挂在工单上，没有模板版本概念，历史工单无法还原。

**修改要求**：

1. **新建 `backend/models/check_template.py`**：

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime

class CheckTemplate(Base):
    __tablename__ = "check_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称，如：桥式起重机月检标准模板")
    category = Column(String(50), nullable=False, comment="适用设备大类")
    version = Column(Integer, nullable=False, default=1, comment="版本号，每次修改自动+1")
    items = Column(Text, nullable=False, comment="检查项JSON，格式：[{name, required, order}]")
    is_active = Column(Boolean, default=True, comment="是否为当前启用版本")
    created_by = Column(Integer, nullable=True, comment="创建人user_id")
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **修改 `backend/models/work_order.py`**，在 WorkOrder 类中添加字段：
```python
template_id = Column(Integer, ForeignKey("check_templates.id"), nullable=True, comment="派单时锁定的检查模板ID")
template_version = Column(Integer, nullable=True, comment="派单时锁定的模板版本号，防止模板变更影响历史记录")
```

3. **在 `backend/models/__init__.py`** 中导入 CheckTemplate。

4. **新建 `backend/routers/template.py`**，实现以下接口：
   - `GET /api/v1/templates` — 获取所有启用中的模板列表
   - `GET /api/v1/templates/{id}` — 获取模板详情及检查项
   - `POST /api/v1/templates` — 新建模板（仅 ADMIN）
   - `PUT /api/v1/templates/{id}` — 更新模板（自动创建新版本，旧版本 is_active=False，仅 ADMIN）

5. **在 `backend/main.py`** 中注册 template 路由。

6. **在 `backend/seed_data.py`** 中添加初始模板数据：
   - 桥式起重机月检模板（包含：主梁、端梁、大车运行机构、小车运行机构、起升机构、制动器、限位开关、钢丝绳 共8个检查项）

**验证**：调用 GET /api/v1/templates，确认返回初始模板数据。

---

### FIX-08：小程序补充水印相机和离线检查表

**目录**：`miniapp/src/`
**现状**：小程序只有 login、index、orderDetail 三个页面，缺少核心现场作业功能。

**修改要求**：

#### 8.1 新建 `miniapp/src/utils/watermark.js`

实现水印叠加工具：
```javascript
/**
 * 给图片添加水印
 * @param {string} tempFilePath - 原始图片临时路径
 * @param {string} address - 地址文字（来自逆地理编码）
 * @returns {Promise<string>} 加了水印的新临时文件路径
 */
export async function addWatermark(tempFilePath, address) {
  return new Promise((resolve, reject) => {
    const now = new Date();
    const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
    
    const canvasId = 'watermark-canvas-' + Date.now();
    
    uni.getImageInfo({ src: tempFilePath, success: (imgInfo) => {
      const width = imgInfo.width;
      const height = imgInfo.height;
      
      const ctx = uni.createCanvasContext(canvasId);
      ctx.drawImage(tempFilePath, 0, 0, width, height);
      
      // 半透明黑色背景条（底部）
      const barHeight = 80;
      ctx.setFillStyle('rgba(0,0,0,0.55)');
      ctx.fillRect(0, height - barHeight, width, barHeight);
      
      // 白色水印文字
      ctx.setFillStyle('#FFFFFF');
      ctx.setFontSize(22);
      ctx.fillText(timeStr, 20, height - barHeight + 28);
      ctx.setFontSize(18);
      ctx.fillText(address || '位置获取中...', 20, height - barHeight + 60);
      
      ctx.draw(false, () => {
        uni.canvasToTempFilePath({
          canvasId,
          fileType: 'jpg',
          quality: 0.9,
          success: (res) => resolve(res.tempFilePath),
          fail: reject
        });
      });
    }, fail: reject });
  });
}
```

#### 8.2 新建 `miniapp/src/utils/offline-queue.js`

实现离线任务队列：
```javascript
const QUEUE_KEY = 'offline_task_queue';

/**
 * 将任务推入离线队列（网络不可用时使用）
 * @param {string} taskType - 任务类型，如 'complete_order'
 * @param {object} data - 任务数据
 */
export function pushToQueue(taskType, data) {
  const queue = uni.getStorageSync(QUEUE_KEY) || [];
  queue.push({ taskType, data, createdAt: Date.now() });
  uni.setStorageSync(QUEUE_KEY, queue);
  console.log(`[离线队列] 已入队：${taskType}，当前队列长度：${queue.length}`);
}

/**
 * 处理离线队列（网络恢复后调用）
 * 从 app.js 的网络状态监听中触发
 */
export async function processQueue() {
  const queue = uni.getStorageSync(QUEUE_KEY) || [];
  if (queue.length === 0) return;
  
  console.log(`[离线队列] 开始处理 ${queue.length} 个待同步任务`);
  const failed = [];
  
  for (const task of queue) {
    try {
      await executeTask(task);
      console.log(`[离线队列] 任务处理成功：${task.taskType}`);
    } catch (err) {
      console.error(`[离线队列] 任务失败：${task.taskType}`, err);
      failed.push(task);
    }
  }
  
  // 只保留失败的任务，等待下次重试
  uni.setStorageSync(QUEUE_KEY, failed);
  
  if (failed.length === 0) {
    uni.showToast({ title: '离线数据已同步', icon: 'success' });
  }
}

async function executeTask(task) {
  const { request } = await import('./request');
  switch (task.taskType) {
    case 'complete_order':
      return request.put(`/orders/${task.data.orderId}/complete`, task.data.payload);
    case 'push_sign':
      return request.put(`/orders/${task.data.orderId}/push_sign`, task.data.payload);
    default:
      console.warn(`[离线队列] 未知任务类型：${task.taskType}`);
  }
}
```

#### 8.3 修改 `miniapp/src/App.vue`

在 app 中监听网络状态，恢复时自动同步：
```javascript
import { processQueue } from './utils/offline-queue';

onLaunch(() => {
  // 监听网络状态变化
  uni.onNetworkStatusChange((res) => {
    if (res.isConnected) {
      console.log('[网络] 已恢复连接，开始同步离线队列');
      processQueue();
    }
  });
});
```

#### 8.4 新建 `miniapp/src/components/watermark-camera/watermark-camera.vue`

水印相机组件，供 inspection 页面调用：
- 调用 `uni.chooseMedia` 拍照
- 同步调用 `uni.getLocation` 获取坐标
- 坐标转文字地址（直接格式化为"经度:XX 纬度:XX"，避免腾讯地图 API Key 依赖问题）
- 调用 `addWatermark()` 生成水印图
- 触发自定义事件 `photoTaken`，传出 `{ filePath, address, lat, lng }`

#### 8.5 新建 `miniapp/src/pages/inspection/inspection.vue`

检查填单页，从 orderDetail 点击"开始检查"后跳转：
- `onLoad` 时先尝试从 Storage 读取缓存模板（`template_cache_{templateId}`）
- 同时发起网络请求拉取最新模板，成功后更新缓存
- 渲染检查项列表：每项显示名称 + 「正常 / 异常」切换按钮
- 选择「异常」时，展开：备注文本框（必填）+ 可选拍照按钮（使用 watermark-camera 组件）
- 所有填写内容实时存入 Storage（key: `draft_inspection_{orderId}`）防丢失
- 底部「提交检查」按钮：校验所有必填项 → 跳转签名页，携带 `orderId` 和 `inspectionData` 参数

#### 8.6 新建 `miniapp/src/pages/signature/signature.vue`

客户签名页：
- 用 Canvas 实现手写签名板（监听 touchstart/touchmove/touchend）
- 「清除」按钮重置画布
- 「确认提交」按钮：将 Canvas 导出为 PNG 临时文件，上传到后端 POST /api/v1/upload/sign，拿到 sign_url 后调用 PUT /orders/{id}/complete 完成工单

#### 8.7 修改 `miniapp/src/pages.json`

注册新增页面：
```json
{
  "path": "pages/inspection/inspection",
  "style": { "navigationBarTitleText": "检查填单" }
},
{
  "path": "pages/signature/signature", 
  "style": { "navigationBarTitleText": "客户签字确认" }
}
```

**验证**：
1. 在微信开发者工具中编译，确认无报错
2. 检查页面能正常渲染检查项列表
3. 关闭网络后填写检查项，确认数据存入 Storage；恢复网络后确认自动同步触发

---

## 🔵 优化项（有时间再做）

---

### OPT-01：切换数据库为 MySQL

**文件**：`crane-mms/.env`（或 `backend/.env`）
**修改**：将 `DATABASE_URL` 从 SQLite 路径改为 MySQL 连接串：
```
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3306/crane_mms
```
并将仓库中的 `crane_mms.db` 文件加入 `.gitignore`：
```
*.db
*.sqlite3
```

---

### OPT-02：备件和维修操作补充审计日志

**文件**：`backend/routers/part.py`、`backend/routers/repair.py`

在所有写操作（入库、出库、创建维修工单、更新维修工单）中补充调用：
```python
from core.audit import write_audit_log
write_audit_log(db=db, user_id=current_user.id, action="CREATE/UPDATE", table_name="parts/repair_orders", record_id=record.id, new_value=data_dict)
```

---

## 执行完成后的验收检查

全部修复完成后，执行以下检查：

```bash
# 1. 运行所有测试
cd crane-mms/backend
pytest tests/ -v
# 期望：全部 PASSED

# 2. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. 依次验证以下接口（用 Swagger UI: http://localhost:8000/docs）
# - 用 Admin@2024 登录 admin 账号 ✓
# - 解码 JWT 确认有效期 24 小时 ✓
# - 调用 GET /orders 确认无报错 ✓
# - 用 manager01 账号登录，调用 GET /customers 确认只看到自己的客户 ✓
# - 调用 GET /templates 确认返回模板数据 ✓
```
