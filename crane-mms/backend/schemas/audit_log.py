from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    log_id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    table_name: str
    record_id: int
    new_value: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
