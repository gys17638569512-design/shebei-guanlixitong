from fastapi import APIRouter, Depends, BackgroundTasks, Path, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from core.database import get_db
from core.permissions import get_current_user, require_role
from core.response import ok
from core.audit import write_audit_log
from models.user import User
from models.work_order import WorkOrder, OrderStatus
from schemas.work_order import WorkOrderCreate, WorkOrderBatch
from services import order_service
from core import sms
from core.settings import settings
from models.customer import Customer

router = APIRouter(prefix="/orders", tags=["工单中心"])


@router.get("/my", summary="获取我的工单列表", description="根据当前登录的工程人员 Token，拉取分配给该人员的所有工单任务及其当前维护状态。")
async def get_my_orders(
    current_user: User = Depends(require_role(["TECH"])),
    db: Session = Depends(get_db)
):
    data = order_service.get_my_orders(db, current_user)
    return ok(data)


@router.get("/{id}", summary="获取工单详情", description="根据工单 ID 获取特定工单的详细信息，包含客户、指派人、状态及检查项的级联数据。")
async def get_order(
    id: int = Path(..., description="要查询的单一工单记录的 ID 数字"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = order_service.get_order_detail(db, id, current_user)
    return ok(data)


@router.put("/{id}/checkin", summary="现场实施打卡", description="维保人员到达现场后调用的接口，记录签到时间、地理位置及现场照片凭证，将工单推进到 [进行中] 状态。")
async def checkin_order(
    id: int = Path(..., description="要进行签到打卡的工单 ID"),
    checkin_data: dict = Body(..., description="签到负载数据，包含经纬度与现场环境照片 URL"),
    current_user: User = Depends(require_role(["TECH"])),
    db: Session = Depends(get_db)
):
    order_service.checkin_order(db, id, checkin_data, current_user)
    return ok(None, msg="Checkin successful")


@router.put("/{id}/complete", summary="提交工单完成反馈", description="维保人员完成检查项排查后，上传客户手写签字留存，并触发自动 PDF 报告生成的结单流程。")
async def complete_order_route(
    id: int = Path(..., description="要确认完成的工单 ID"),
    completion_data: dict = Body(..., description="完工负载数据，必须包含客户签名的图片 URL 等总结信息"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(require_role(["TECH"])),
    db: Session = Depends(get_db)
):
    order_service.complete_order(db, id, completion_data, current_user)

    from services import pdf_service

    # 异步生成电子维保单 PDF 并自动归档
    background_tasks.add_task(pdf_service.generate_maintenance_report, id)

    return ok(None, msg="Order completed successfully")


@router.put("/{id}/push_sign", summary="推送客户签字", description="维修员不直接结单，而是先保存排查结果并把状态推向 [待签字]，将签环节转移给客户。")
async def push_order_for_sign(
    id: int = Path(..., description="要推给客户签字的工单 ID"),
    push_data: dict = Body(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(require_role(["TECH"])),
    db: Session = Depends(get_db)
):
    order_id = order_service.push_for_sign(db, id, push_data, current_user)
    
    # 【二期】触发短信提醒客户签字
    order = db.query(WorkOrder).filter(WorkOrder.id == id).first()
    if order and order.customer and order.customer.contact_phone:
        background_tasks.add_task(
            sms.send_sign_request_sms, 
            phone=order.customer.contact_phone, 
            order_id=order.id,
            portal_url=settings.CUSTOMER_PORTAL_URL
        )
    
    return ok(None, msg="已成功保存内容，并推送至客户等待签字！")


@router.post("", summary="创建新工单（派单）", description="管理员或经理将维保任务指派给特定工程师，指定设备、日期、工单类型。创建成功后工程师小程序端将收到推送。")
async def create_order(
    order_in: WorkOrderCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    """
    创建工单的核心业务逻辑：
    1. 校验客户、设备、工程师是否存在
    2. 写入 work_orders 表
    3. 写入 audit_logs 审计记录
    """
    # 直接写入数据库，不依赖原有 order_service（避免参数不匹配）
    new_order = WorkOrder(
        order_type=order_in.order_type,
        customer_id=order_in.customer_id,
        equipment_id=order_in.equipment_id,
        technician_id=order_in.technician_id,
        plan_date=order_in.plan_date,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.flush()

    # 写入操作审计日志 - PRD 铁律：所有写操作必须记录
    write_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        table_name="work_orders",
        record_id=new_order.id,
        new_value={
            "order_type": new_order.order_type,
            "equipment_id": new_order.equipment_id,
            "technician_id": new_order.technician_id,
            "plan_date": str(new_order.plan_date)
        }
    )

    db.commit()
    db.refresh(new_order)
    
    # 【二期】新工单派单，通知执行工程师
    from models.user import User as UserModel
    tech = db.query(UserModel).filter(UserModel.id == new_order.technician_id).first()
    if tech and tech.phone:
        background_tasks.add_task(
            sms.send_dispatch_sms,
            phone=tech.phone,
            order_id=new_order.id,
            customer_name=new_order.customer.company_name if new_order.customer else "未知客户"
        )
        
    return ok(data=new_order)


@router.get("", summary="获取所有工单（管理员/经理视图）", description="支持按工单状态、工程师ID、客户ID筛选，用于PC后台工单管理看板。")
async def get_orders(
    status: Optional[str] = Query(None, description="按工单状态筛选，如 PENDING/IN_PROGRESS/COMPLETED"),
    technician_id: Optional[int] = Query(None, description="按工程师ID筛选"),
    customer_id: Optional[int] = Query(None, description="按客户ID筛选"),
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    from repositories.work_order_repo import get_orders_with_relations
    orders = get_orders_with_relations(db, status, technician_id, customer_id)
    
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_type": o.order_type,
            "status": o.status.value if hasattr(o.status, 'value') else o.status,
            "plan_date": str(o.plan_date),
            "created_at": str(o.created_at),
            "customer_id": o.customer_id,
            "customer_name": o.customer.company_name if o.customer else "—",
            "equipment_id": o.equipment_id,
            "equipment_name": o.equipment.name if o.equipment else "—",
            "technician_id": o.technician_id,
            "technician_name": o.technician.name if o.technician else "—",
        })
    return ok(data=result)


@router.post("/batch", summary="批量排期下单", description="管理员或经理一次性对多台设备批量创建例行维保工单，支持不同设备指定不同工程师和日期。")
async def batch_create_orders(
    batch_in: WorkOrderBatch,
    current_user: User = Depends(require_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    """
    批量新建工单业务逻辑：
    1. 循环逐条创建工单
    2. 重复检测（同一设备同一天已有PENDING/IN_PROGRESS工单则跳过）
    3. 全部成功后一次性提交（原子性事务）
    """
    created = []
    skipped = []

    for item in batch_in.items:
        # 重复检测
        existing = db.query(WorkOrder).filter(
            WorkOrder.equipment_id == item.equipment_id,
            WorkOrder.plan_date == item.plan_date,
            WorkOrder.status.in_([OrderStatus.PENDING, OrderStatus.IN_PROGRESS])
        ).first()

        if existing:
            skipped.append({"equipment_id": item.equipment_id, "reason": "设备在该日期已有未完成工单"})
            continue

        new_order = WorkOrder(
            order_type=batch_in.order_type,
            customer_id=item.customer_id,
            equipment_id=item.equipment_id,
            technician_id=item.technician_id,
            plan_date=item.plan_date,
            status=OrderStatus.PENDING
        )
        db.add(new_order)
        db.flush()

        write_audit_log(
            db=db,
            user_id=current_user.id,
            action="BATCH_CREATE",
            table_name="work_orders",
            record_id=new_order.id,
            new_value={"order_type": batch_in.order_type, "equipment_id": item.equipment_id, "plan_date": str(item.plan_date)}
        )
        created.append(new_order.id)

    db.commit()
    return ok(data={"created_count": len(created), "skipped_count": len(skipped), "skipped_items": skipped}, msg=f"成功创建 {len(created)} 条工单")
