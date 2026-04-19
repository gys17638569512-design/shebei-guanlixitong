# GPT-5.3-Codex-Low Local Memory

## 用途
这个目录用于保存与本项目协作的本地化记忆，方便换电脑后快速恢复上下文。

## 当前项目协作结论（截至 2026-04-01）
- 当前实施范围：只做管理端 Web（`frontend-pc`）。
- 必须预留：客户端 Web、管理端/客户端微信小程序、电子签名、外部插件接口（短信、存储、消息、地图等）。
- 方法论：6A（Align / Architect / Atomize / Assign / Audit / Accelerate）。
- 已完成计划文件：
  - `c:\Users\郭永盛\.cursor\plans\全局web端6a计划_8a385629.plan.md`

## 换电脑后的恢复步骤
1. 把本目录完整复制到新电脑的同一项目目录下。
2. 打开并先阅读：
   - `gpt-5.3-codex-low-memory\SESSION_MEMORY.md`
   - `c:\Users\郭永盛\.cursor\plans\全局web端6a计划_8a385629.plan.md`（如果路径变化，先在新机定位该计划文件）
3. 在新会话中告诉智能体：
   - “先读取 `gpt-5.3-codex-low-memory\SESSION_MEMORY.md` 和 6A计划文件，再继续执行。”
4. 继续按计划的“首轮执行顺序”推进派工。

## 维护规则
- 每次关键决策变更后，更新 `SESSION_MEMORY.md`。
- 如果计划文件名变化，务必同步更新本目录中的路径记录。
