from core.settings import settings
from models.work_order import WorkOrder
from sqlalchemy.orm import Session
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)


def complete_esign(order_id: int, pdf_path: str, signer_name: str, db: Session) -> str:
    """完整流程：上传文件→创建签署流程→返回签署证书URL"""
    try:
        # 检查是否开启Mock模式
        if settings.ESIGN_MOCK:
            # Mock模式下直接返回模拟URL
            mock_url = f"https://mock-esign.example.com/cert/{order_id}"
            # 更新数据库
            order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
            if order:
                order.esign_cert_url = mock_url
                db.commit()
            return mock_url
        
        # 真实调用e签宝API
        # 这里需要根据e签宝开放平台API文档实现
        # 由于是示例，这里模拟API调用
        logging.info(f"调用e签宝API为工单 {order_id} 创建签署流程")
        
        # 模拟网络请求延迟
        time.sleep(1)
        
        # 模拟返回签署证书URL
        esign_url = f"https://esign.example.com/cert/{order_id}"
        
        # 更新数据库
        order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
        if order:
            order.esign_cert_url = esign_url
            db.commit()
        
        return esign_url
    except Exception as e:
        logging.error(f"e签宝签署失败: {e}")
        # 重试3次
        for i in range(3):
            try:
                logging.info(f"重试第 {i+1} 次")
                time.sleep(2)
                # 再次尝试
                if settings.ESIGN_MOCK:
                    mock_url = f"https://mock-esign.example.com/cert/{order_id}"
                    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
                    if order:
                        order.esign_cert_url = mock_url
                        db.commit()
                    return mock_url
                else:
                    time.sleep(1)
                    esign_url = f"https://esign.example.com/cert/{order_id}"
                    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
                    if order:
                        order.esign_cert_url = esign_url
                        db.commit()
                    return esign_url
            except Exception as retry_e:
                logging.error(f"重试失败: {retry_e}")
                continue
        
        # 全部失败后抛出异常
        raise Exception("e签宝签署失败，请稍后重试")