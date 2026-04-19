# Chat Export Guide

## 目标
尽可能在换电脑后恢复：
- 聊天上下文
- 已完成工作
- 当前计划状态
- 下一步执行口令

## 一次性准备（当前电脑）
1. 保留以下本地记忆目录（必须）：
   - `gpt-5.3-codex-low-memory/README.md`
   - `gpt-5.3-codex-low-memory/SESSION_MEMORY.md`
   - `gpt-5.3-codex-low-memory/CHANGELOG.md`
2. 保留计划文件路径记录（必须）：
   - `c:\Users\郭永盛\.cursor\plans\全局web端6a计划_8a385629.plan.md`
3. 每次阶段结束执行一次“记忆快照”（见文末模板）。

## 每次换电脑前（建议执行）
1. 更新 `SESSION_MEMORY.md`：
   - 当前范围
   - 已完成事项
   - 阻塞项
   - 下一步
2. 更新 `CHANGELOG.md`：
   - 新增当日条目（不要覆盖历史）
3. 复制整个目录：
   - `gpt-5.3-codex-low-memory`
4. 如可访问会话转录文件（可选增强）：
   - 额外导出最近会话标题与摘要到 `CHANGELOG.md`
   - 避免只依赖原始平台会话历史

## 换电脑后恢复流程（标准）
1. 将 `gpt-5.3-codex-low-memory` 复制到新电脑项目根目录。
2. 在新会话首条指令中输入：
   - “先读取 `gpt-5.3-codex-low-memory/SESSION_MEMORY.md`、`gpt-5.3-codex-low-memory/CHANGELOG.md` 和 6A 计划文件，再继续。”
3. 让智能体先复述：
   - 当前范围
   - 已完成
   - 下一步 3 项
4. 你确认后再开始执行。

## 可靠性说明
- 该机制保证“工作连续性”高可恢复。
- 不保证平台侧“所有聊天原文”100%自动同步。
- 如需接近完整恢复，必须坚持“每阶段快照”。

## 记忆快照模板（复制到 CHANGELOG）
```markdown
### 记忆快照
- 当前范围：
- 今日完成：
- 当前阻塞：
- 风险与待确认：
- 下一步3项：
- 关键文件变更：
```
