from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from core.database import get_db
from core.permissions import get_current_user, require_permission
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
        
@router.get("/reports/archive", summary="获取所有已归档报告", description="拉取所有具备 PDF 连接的已完成工单列表")
async def get_report_archive(
    current_user: User = Depends(require_permission("settings.reports.access")),
    db: Session = Depends(get_db)
):
    from core.response import ok
    orders = db.query(WorkOrder).filter(WorkOrder.pdf_report_url != None).order_by(WorkOrder.completed_at.desc()).all()
    result = []
    for order in orders:
        result.append({
            "order_id": order.id,
            "equipment_name": order.equipment.name if order.equipment else "未知设备",
            "customer_name": order.customer.company_name if order.customer else "未知客户",
            "completed_at": str(order.completed_at) if order.completed_at else None,
            "pdf_url": order.pdf_report_url,
            "esign_cert_url": order.esign_cert_url
        })
    return ok(data=result)
