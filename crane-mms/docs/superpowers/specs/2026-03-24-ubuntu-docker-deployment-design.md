# Ubuntu Docker Deployment Design

**Goal:** 为项目建立一套可在 Ubuntu 24.04 64 位内网服务器上稳定运行的生产部署方案，使用 Docker 容器和自建 MySQL，并保留完整部署记录以便聊天丢失后恢复续接。

**Current Context**

- 项目目录包含 `backend`、`frontend-pc`、`frontend-portal`、`miniapp`
- 后端为 FastAPI + SQLAlchemy，依赖 MySQL
- 前端 PC 与客户门户均为 Vite 构建的静态站点
- 生产环境基线已确认：
  - Ubuntu 24.04 LTS 64 位
  - Docker / Docker Compose
  - MySQL 容器自建
  - 内网部署
- 测试环境是 Windows ECS，仅用于验证，不作为正式标准部署形态

## Deployment Approaches

### Approach 1: 单机 Docker Compose 一体化部署

在一台 Ubuntu 主机上运行 `mysql`、`backend`、`nginx` 三类服务，前端在镜像构建阶段编译为静态资源并复制到 `nginx` 容器内。

优点：

- 最贴合当前项目阶段，部署和运维复杂度最低
- 回滚简单，适合内网首版生产
- 便于记录和标准化

缺点：

- 所有核心服务集中在单机，扩展能力有限
- MySQL 与应用同主机时资源竞争更明显

### Approach 2: 应用容器化，数据库独立宿主或独立实例

应用仍用 Docker Compose，MySQL 改为独立实例。

优点：

- 数据与应用解耦，更利于后续扩展与备份
- 数据库风险隔离更好

缺点：

- 当前用户已明确要求自建 MySQL 容器，这条不作为本轮主方案

### Approach 3: Kubernetes / 多节点编排

优点：

- 适合更复杂的生产体系

缺点：

- 明显超出当前项目和服务器阶段需要
- 运维成本过高，不符合 YAGNI

## Recommendation

本轮推荐 **Approach 1：单机 Docker Compose 一体化部署**。

原因：

- 与用户确认的 Ubuntu + Docker + 自建 MySQL 完全一致
- 当前项目最需要的是一套稳定、可复现、可回滚、可记录的生产基线
- 后续若要升级到多机或独立数据库，也可以在现有 Compose 结构上平滑演进

## Architecture

生产环境采用单机内网容器架构：

- `mysql` 容器：提供业务数据库，数据目录使用宿主机卷持久化
- `backend` 容器：运行 FastAPI 服务，仅暴露容器内部端口给 `nginx`
- `nginx` 容器：统一入口
  - 反代 `/api/` 到 `backend`
  - 托管 `frontend-pc` 静态资源
  - 托管 `frontend-portal` 静态资源
- Docker 自定义网络负责服务间通信

内网访问建议：

- PC 后台使用一个内网域名或路径前缀
- 客户门户使用单独内网域名或单独站点路径
- 若短期无域名，可先以内网 IP + 端口验证，再补域名映射

## Container Responsibilities

### mysql

- 基于官方 MySQL 8 镜像
- 使用持久化卷保存：
  - `/var/lib/mysql`
- 使用初始化环境变量建立业务库与业务账号
- 不对外网开放，仅在内网或 Docker 网络中可达

### backend

- 基于 Python 3.12 镜像
- 安装 `backend/requirements.txt`
- 从 `.env` 读取生产配置
- 运行命令建议为 `uvicorn main:app --host 0.0.0.0 --port 8001`
- 挂载上传目录与运行日志目录

### nginx

- 基于官方 Nginx 镜像
- 提供两类能力：
  - 静态文件服务
  - `/api` 反向代理
- 挂载自定义 Nginx 配置
- 可选挂载访问日志和错误日志目录

## Frontend Delivery

前端不需要单独运行 Node 进程。推荐多阶段镜像构建：

- 在构建阶段使用 Node 安装依赖并执行 `npm run build`
- 将 `frontend-pc/dist` 与 `frontend-portal/dist` 复制到最终 `nginx` 镜像

这样可以：

- 减少运行态容器数量
- 降低生产环境复杂度
- 减少 Node 在生产环境中的资源占用

## Data and Persistence

宿主机建议保留统一部署根目录，例如：

- `/srv/crane-mms/mysql`
- `/srv/crane-mms/uploads`
- `/srv/crane-mms/logs`
- `/srv/crane-mms/deploy`

持久化策略：

- MySQL 数据持久化到宿主机卷
- 后端上传文件持久化到宿主机卷
- 日志保留到宿主机卷，便于排查和恢复

## Environment Variables

后端最少需要：

- `DATABASE_URL`
- `SECRET_KEY`

推荐同时梳理：

- `CUSTOMER_PORTAL_URL`
- COS 配置
- e签宝配置
- 短信配置
- 微信配置

原则：

- 不在镜像里写死敏感信息
- 使用生产 `.env` 文件或 Compose 环境变量注入
- 密码与密钥只记录字段名，不在恢复记录中保存明文

## Recovery Record Strategy

为避免聊天记录丢失导致无法续接，部署流程必须同步写入仓库内文档：

- 部署设计文档
- 实施计划文档
- 实际部署记录文档

实际部署记录至少包含：

- 服务器角色与系统信息
- 目录规划
- Docker / Compose 版本
- 镜像标签
- `.env` 字段清单
- 启停命令
- 验证结果
- 回滚步骤

建议目标文件：

- `docs/deployment/2026-03-24-ubuntu-production-deploy-record.md`

## Risks and Mitigations

### 风险 1：2 套前端路径冲突

缓解：

- 设计清晰的站点映射
- 优先使用两个内网域名
- 若只能单域名，则通过清晰路径前缀隔离

### 风险 2：MySQL 容器数据丢失

缓解：

- 强制使用宿主机持久卷
- 部署完成后补自动备份脚本或手工备份流程

### 风险 3：环境变量不完整导致容器启动失败

缓解：

- 在部署前先整理 `.env.production.example`
- 启动前执行配置校验清单

### 风险 4：后端上传目录与 Nginx 静态访问路径不一致

缓解：

- 在 Compose 中统一挂载路径
- 在部署验收时加入上传/下载链路验证

## Testing and Verification

正式上线前至少验证：

- `docker compose config` 成功
- `docker compose up -d` 成功
- MySQL 容器健康
- backend 容器健康
- Nginx 容器健康
- `/health` 接口可访问
- 前端首页可访问
- 登录链路可验证
- 静态资源 200
- API 反代 200

## Approval Summary

用户已确认：

- Windows ECS 仅作测试用途
- 正式生产环境使用 Ubuntu 24.04 64 位
- 使用 Docker 容器
- MySQL 自建容器
- 内网部署

基于以上确认，下一步进入实施计划编写阶段。
