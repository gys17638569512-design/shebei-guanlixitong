from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.response import ok
from schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from services.equipment_service import EquipmentService
from core.permissions import get_current_user
from models.user import User

router = APIRouter(
    prefix="/equipments",
    tags=["设备档案"]
)

@router.post("", summary="新建设备并保存部件清单")
def create_equipment(
    equipment_in: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 写操作，传入 user_id 以记录审计日志
    service = EquipmentService(db)
    equipment = service.create_equipment(equipment_in, current_user.id)
    return ok(data=equipment)

@router.get("", summary="获取设备列表", description="支持按应轷盟筛选或名称搜索的全量设备应云列表。")
def get_equipments(
    search: str = Query(None, description="按设备名称模糊搜索"),
    customer_id: int = Query(None, description="按客户ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = EquipmentService(db)
    items = service.get_equipment_list(search=search, customer_id=customer_id)
    return ok(data=items)

@router.get("/templates", summary="根据大类和型式智能获取部件清单模板")
def get_equipment_templates(
    category: str = Query(..., description="设备大类"),
    model_type: str = Query(..., description="型式"),
    tonnage: str = Query(None, description="吨位"),
    span: str = Query(None, description="跨度"),
    manufacturer: str = Query(None, description="厂家"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 读操作，无需审计日志
    service = EquipmentService(db)
    templates = service.template_service.get_compatible_parts(category, model_type, tonnage, span, manufacturer)
    return ok(data=templates)

@router.get("/{equipment_id}", summary="获取设备档案详情（含部件清单）")
def get_equipment_detail(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 读操作，无需审计日志
    service = EquipmentService(db)
    equipment = service.get_equipment_detail(equipment_id)
    return ok(data=equipment)

@router.put("/{equipment_id}", summary="更新设备档案信息")
def update_equipment(
    equipment_id: int,
    equipment_in: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 写操作，传入 user_id 以记录审计日志
    service = EquipmentService(db)
    equipment = service.update_equipment(equipment_id, equipment_in, current_user.id)
    return ok(data=equipment)
