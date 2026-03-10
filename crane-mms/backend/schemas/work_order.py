from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from models.work_order import OrderStatus

class WorkOrderCreate(BaseModel):
    """创建工单时前端提交的数据结构"""
    equipment_id: int = Field(..., description="关联设备ID")
    customer_id: int = Field(..., description="关联客户ID")
    technician_id: int = Field(..., description="执行工程师用户ID")
    order_type: str = Field(..., description="工单类型：周检/月检/季检/年检/临时维保")
    plan_date: date = Field(..., description="计划维保日期")

    class Config:
        json_schema_extra = {
            "example": {
                "equipment_id": 1,
                "customer_id": 1,
                "technician_id": 2,
                "order_type": "月检",
                "plan_date": "2024-04-15"
            }
        }

class WorkOrderResponse(BaseModel):
    """工单列表/详情接口的返回格式"""
    id: int
    order_type: str
    customer_id: int
    equipment_id: int
    technician_id: int
    plan_date: date
    status: str
    # 关联数据（嵌套返回，前端可以直接使用）
    customer_name: Optional[str] = None
    equipment_name: Optional[str] = None
    technician_name: Optional[str] = None

    class Config:
        from_attributes = True

class WorkOrderBatchItem(BaseModel):
    """批量排期中单条工单的配置"""
    equipment_id: int = Field(..., description="关联设备ID")
    customer_id: int = Field(..., description="关联客户ID")
    technician_id: int = Field(..., description="指派工程师用户ID")
    plan_date: date = Field(..., description="计划维保日期")

class WorkOrderBatch(BaseModel):
    """批量创建工单请求体"""
    order_type: str = Field(..., description="统一工单类型：周检/月检/季检/年检")
    items: List[WorkOrderBatchItem] = Field(..., description="批量工单条目列表，每条对应一台设备")

    class Config:
        json_schema_extra = {
            "example": {
                "order_type": "月检",
                "items": [
                    {"equipment_id": 1, "customer_id": 1, "technician_id": 2, "plan_date": "2024-04-15"},
                    {"equipment_id": 2, "customer_id": 1, "technician_id": 2, "plan_date": "2024-04-15"}
                ]
            }
        }
