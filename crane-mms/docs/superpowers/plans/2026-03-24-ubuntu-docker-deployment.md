# Ubuntu Docker Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `crane-mms` 项目补齐 Ubuntu 24.04 内网生产环境所需的 Docker 化部署资产、配置模板与恢复记录模板。

**Architecture:** 使用单机 Docker Compose 编排 `mysql`、`backend`、`nginx` 三类服务；前端在构建阶段生成静态资源并由 `nginx` 托管；所有敏感配置通过 `.env` 注入，数据与上传目录通过宿主机卷持久化。

**Tech Stack:** Docker, Docker Compose, MySQL 8, Nginx, Python 3.12, FastAPI, Vue/Vite

---

### Task 1: 梳理部署文件结构

**Files:**
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\docker-compose.yml`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\.env.production.example`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\nginx.conf`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\backend.Dockerfile`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\frontend-nginx.Dockerfile`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\docs\deployment\2026-03-24-ubuntu-production-deploy-record.md`

- [ ] **Step 1: 确认现有仓库没有可复用的生产部署目录**

Run: `Get-ChildItem 'C:\Users\郭永盛\Documents\设备管理系统\crane-mms' -Recurse | Select-String -Pattern 'docker-compose|Dockerfile|nginx.conf'`
Expected: 了解现有部署资产是否缺失或需要复用

- [ ] **Step 2: 明确每个文件职责**

Expected:
- `docker-compose.yml` 负责服务编排
- `.env.production.example` 负责字段模板
- `nginx.conf` 负责站点与反代
- `backend.Dockerfile` 负责后端镜像
- `frontend-nginx.Dockerfile` 负责前端构建并集成到 Nginx
- 部署记录文档负责续接和回滚

- [ ] **Step 3: 提交结构设计说明到文档或执行记录**

Expected: 后续执行者无需重新猜测目录结构

### Task 2: 编写后端容器镜像

**Files:**
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\backend.Dockerfile`
- Modify: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\backend\requirements.txt`

- [ ] **Step 1: 写一个最小镜像构建方案**

Expected:
- 以 Python 3.12 为基础镜像
- 工作目录指向 `/app/backend`
- 先复制依赖文件，再安装依赖，再复制代码

- [ ] **Step 2: 明确启动命令**

Expected:
- `uvicorn main:app --host 0.0.0.0 --port 8001`

- [ ] **Step 3: 检查是否存在 Linux 容器不兼容依赖**

Run: `Get-Content -Raw 'C:\Users\郭永盛\Documents\设备管理系统\crane-mms\backend\requirements.txt'`
Expected: 如有系统依赖，在 Dockerfile 中补充安装说明

- [ ] **Step 4: 验证 Dockerfile 至少在语义上完整**

Expected: 有基础镜像、依赖安装、代码复制、启动命令

### Task 3: 编写前端 Nginx 镜像

**Files:**
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\frontend-nginx.Dockerfile`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\nginx.conf`

- [ ] **Step 1: 为 `frontend-pc` 和 `frontend-portal` 设计多阶段构建**

Expected:
- Node 阶段构建两个前端
- Nginx 阶段复制两个 `dist`

- [ ] **Step 2: 设计站点映射**

Expected:
- 支持双域名，或在单域名下通过路径前缀区分
- `/api/` 反代到 backend

- [ ] **Step 3: 在 Nginx 配置中加入前端 SPA 刷新回退**

Expected:
- 直接访问前端深链路时返回对应 `index.html`

- [ ] **Step 4: 明确上传目录与静态站点分离**

Expected: 避免 `uploads` 与前端静态资源混淆

### Task 4: 编写 Compose 编排和环境变量模板

**Files:**
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\docker-compose.yml`
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\deploy\docker\.env.production.example`

- [ ] **Step 1: 定义 `mysql` 服务**

Expected:
- 指定镜像版本
- 配置库名、用户、密码变量
- 配置数据卷
- 配置健康检查

- [ ] **Step 2: 定义 `backend` 服务**

Expected:
- 依赖 `mysql`
- 通过环境变量注入 `DATABASE_URL` 等字段
- 挂载上传目录和日志目录

- [ ] **Step 3: 定义 `nginx` 服务**

Expected:
- 对外暴露内网访问端口
- 依赖 `backend`
- 加载 `nginx.conf`

- [ ] **Step 4: 编写 `.env.production.example`**

Expected:
- 包含数据库、JWT、门户地址、三方服务字段
- 不写真实密码

- [ ] **Step 5: 运行 Compose 语义校验**

Run: `docker compose -f deploy/docker/docker-compose.yml config`
Expected: 配置展开成功，无语法错误

### Task 5: 编写部署记录与回滚模板

**Files:**
- Create: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\docs\deployment\2026-03-24-ubuntu-production-deploy-record.md`

- [ ] **Step 1: 写入服务器基线信息**

Expected:
- Ubuntu 24.04 64 位
- 内网
- Docker 化部署

- [ ] **Step 2: 写入目录规划**

Expected:
- `/srv/crane-mms/mysql`
- `/srv/crane-mms/uploads`
- `/srv/crane-mms/logs`
- `/srv/crane-mms/deploy`

- [ ] **Step 3: 写入启动、停机、重启、回滚命令模板**

Expected: 后续聊天丢失时可直接续接执行

- [ ] **Step 4: 写入验收清单**

Expected:
- 容器状态
- API 健康检查
- 前端访问
- 数据库连接
- 上传链路

### Task 6: 生成交付说明并准备执行

**Files:**
- Modify: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\docs\superpowers\specs\2026-03-24-ubuntu-docker-deployment-design.md`
- Modify: `C:\Users\郭永盛\Documents\设备管理系统\crane-mms\docs\superpowers\plans\2026-03-24-ubuntu-docker-deployment.md`

- [ ] **Step 1: 核对设计与计划一致**

Expected: 架构、文件、服务职责不冲突

- [ ] **Step 2: 明确执行前还需用户提供的信息**

Expected:
- 内网域名或访问方式
- 实际服务器连接方式
- 是否部署两个前端
- 生产密码与密钥填充值

- [ ] **Step 3: 进入执行选择**

Expected: 决定由子智能体逐任务执行，还是当前会话内联执行
