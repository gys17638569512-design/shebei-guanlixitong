from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.response import ok
from core.permissions import require_role
from models.user import User
from models.check_template import CheckTemplate
import json

router = APIRouter(
    prefix="/templates",
    tags=["检查模板管理"]
)

@router.get("", summary="获取所有启用中的模板列表")
def get_templates(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(CheckTemplate).filter(CheckTemplate.is_active == True)
    if category:
        query = query.filter(CheckTemplate.category == category)
    templates = query.all()
    
    # 解析 items JSON
    for t in templates:
        t.items = json.loads(t.items) if isinstance(t.items, str) else t.items
        
    return ok(data=templates)

@router.get("/{template_id}", summary="获取模板详情")
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    template = db.query(CheckTemplate).filter(CheckTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    template.items = json.loads(template.items) if isinstance(template.items, str) else template.items
    return ok(data=template)

@router.post("", summary="新建模板 (仅限管理员)")
def create_template(
    name: str,
    category: str,
    items: List[dict],
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    new_template = CheckTemplate(
        name=name,
        category=category,
        items=json.dumps(items, ensure_ascii=False),
        version=1,
        is_active=True,
        created_by=current_user.id
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return ok(data=new_template, msg="模板已创建")

@router.put("/{template_id}", summary="更新模板 (自动创建新版本)")
def update_template(
    template_id: int,
    name: str,
    category: str,
    items: List[dict],
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    old_template = db.query(CheckTemplate).filter(CheckTemplate.id == template_id).first()
    if not old_template:
        raise HTTPException(status_code=404, detail="原模板不存在")
    
    # 停用旧版本
    old_template.is_active = False
    
    # 创建新版本
    new_template = CheckTemplate(
        name=name,
        category=category,
        items=json.dumps(items, ensure_ascii=False),
        version=old_template.version + 1,
        is_active=True,
        created_by=current_user.id
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return ok(data=new_template, msg="模板已更新为新版本")
