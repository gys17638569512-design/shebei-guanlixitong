from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from core.database import get_db
from core.permissions import get_current_user
from models.user import User
from models.work_order import WorkOrder

router = APIRouter(prefix="/orders", tags=["报告生成"])


@router.get("/{id}/report", summary="获取工单维护报告PDF", description="拉取已完成工单生成的最终 PDF 纸质格式报告链接，及其关联的电子签名凭证链。")
async def get_order_report(
    id: int = Path(..., description="要获取 PDF 报告的工单 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(WorkOrder).filter(WorkOrder.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 权限检查
    if current_user.role == "TECH" and order.technician_id != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if order.pdf_report_url:
        return {
            "pdf_url": order.pdf_report_url,
            "esign_cert_url": order.esign_cert_url
        }
    else:
        return {"status": "generating"}