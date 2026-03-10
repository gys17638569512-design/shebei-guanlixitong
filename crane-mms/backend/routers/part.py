from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.permissions import require_role
from core.response import ok
from models.part import Part
from schemas.part import PartResponse, PartCreate, PartUpdate, PartStockAdjust

router = APIRouter(prefix="/parts", tags=["备件管理"])

@router.get("", summary="获取所有备品备件列表", description="用于在结单时展示可供抵扣的零件池", response_model=None)
async def get_all_parts(db: Session = Depends(get_db)):
    parts = db.query(Part).all()
    
    # 临时插入 mock 数据点，仅在没有任何备件时初始化
    if not parts:
        mock_parts = [
            Part(part_no="PT-1001", name="起升制动器摩擦片", specification="Φ200mm", unit="片", stock_quantity=50, warning_threshold=10, price=120.0),
            Part(part_no="PT-1002", name="钢丝绳润滑脂", specification="L-CKD 320 10kg/桶", unit="桶", stock_quantity=20, warning_threshold=5, price=300.0),
            Part(part_no="PT-1003", name="断火限位器接点", specification="LX10-11", unit="个", stock_quantity=30, warning_threshold=5, price=45.0),
            Part(part_no="PT-2004", name="聚氨酯缓冲器", specification="JHQ-2 150x150", unit="件", stock_quantity=15, warning_threshold=3, price=280.0)
        ]
        db.add_all(mock_parts)
        db.commit()
        parts = db.query(Part).all()
        
    result = [{
        "id": p.id,
        "part_no": p.part_no,
        "name": p.name,
        "specification": p.specification,
        "unit": p.unit,
        "stock_quantity": p.stock_quantity,
        "warning_threshold": p.warning_threshold,
        "price": p.price
    } for p in parts]
    
    return ok(data=result)

@router.post("", summary="录入新备件")
def create_part(
    payload: PartCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "MANAGER"]))
):
    from core.exceptions import BusinessError
    from core.audit import write_audit_log
    
    # 检查重名或重编号
    existing = db.query(Part).filter(Part.part_no == payload.part_no).first()
    if existing:
        raise BusinessError("零件编号已存在")
        
    new_part = Part(**payload.model_dump())
    db.add(new_part)
    db.flush()
    
    write_audit_log(db, current_user.id, "CREATE", "parts", new_part.id, payload.model_dump())
    db.commit()
    db.refresh(new_part)
    return ok(data=new_part)

@router.put("/{part_id}", summary="修改备件信息")
def update_part(
    part_id: int,
    payload: PartUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "MANAGER"]))
):
    from core.exceptions import NotFoundError
    from core.audit import write_audit_log
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise NotFoundError("备件不存在")
        
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(part, k, v)
        
    db.flush()
    write_audit_log(db, current_user.id, "UPDATE", "parts", part.id, update_data)
    db.commit()
    db.refresh(part)
    return ok(data=part)

@router.put("/{part_id}/stock", summary="库存调整(入库/出库)")
def adjust_part_stock(
    part_id: int,
    payload: PartStockAdjust,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(["ADMIN", "MANAGER", "TECH"]))
):
    from core.exceptions import NotFoundError, BusinessError
    from core.audit import write_audit_log
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise NotFoundError("备件不存在")
        
    old_stock = part.stock_quantity
    if payload.action == "in":
        part.stock_quantity += payload.quantity
    elif payload.action == "out":
        if part.stock_quantity < payload.quantity:
            raise BusinessError(f"库存不足，当前仅剩 {part.stock_quantity}")
        part.stock_quantity -= payload.quantity
    else:
        raise BusinessError("无效的操作类型(仅支持 in/out)")
        
    db.flush()
    write_audit_log(
        db, current_user.id, f"STOCK_{payload.action.upper()}", "parts", part.id, 
        {"old_qty": old_stock, "change": payload.quantity, "new_qty": part.stock_quantity}
    )
    db.commit()
    return ok(data=part)
