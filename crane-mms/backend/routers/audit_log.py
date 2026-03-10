from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.audit_log import AuditLog
from models.user import User

router = APIRouter(prefix="/audit-logs", tags=["安全审计"])

@router.get("", summary="获取安全审计日志", description="供管理员检索系统内的敏感操作记录，支持按操作类型、表名、记录ID及操作人过滤。")
async def get_audit_logs(
    action: Optional[str] = Query(None, description="操作类型: CREATE/UPDATE/DELETE"),
    table_name: Optional[str] = Query(None, description="目标表名"),
    user_id: Optional[int] = Query(None, description="操作人ID"),
    limit: int = Query(100, description="返回记录条数限制"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    
    if action:
        query = query.filter(AuditLog.action == action)
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
        
    logs = query.order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "log_id": log.log_id,
            "user_id": log.user_id,
            "user_name": log.user.name if log.user else "未知用户",
            "action": log.action,
            "table_name": log.table_name,
            "record_id": log.record_id,
            "new_value": log.new_value,
            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return ok(data=result)
