import json
from sqlalchemy.orm import Session
from models.audit_log import AuditLog

def write_audit_log(db: Session, user_id: int, action: str, table_name: str, record_id: int, new_value: dict = None):
    """
    记录操作审计日志
    """
    log_entry = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        new_value=json.dumps(new_value, ensure_ascii=False) if new_value else None
    )
    db.add(log_entry)
    db.flush()  # We flush here, caller must commit
