import logging
from core.settings import settings

logger = logging.getLogger("esign")

class ESignService:
    """
    E签宝 / 契约锁 电子签章服务封装
    """
    def __init__(self):
        self.enabled = settings.ESIGN_ENABLED
        self.app_id = settings.ESIGN_APP_ID
        self.app_secret = settings.ESIGN_APP_SECRET
        self.mock_mode = not (self.app_id and self.app_secret)

    async def create_flow(self, order_id: int, pdf_path: str, signers: list):
        """
        发起签署流程
        signers: [{"name": "xxx", "phone": "138...", "role": "CUSTOMER"}]
        """
        if self.mock_mode:
            logger.info(f"[MOCK ESIGN] 为工单 #{order_id} 发起签署流程")
            logger.info(f"[MOCK ESIGN] 文件路径: {pdf_path}")
            return {
                "flow_id": f"flow_mock_{order_id}",
                "short_url": f"{settings.CUSTOMER_PORTAL_URL}/sign/{order_id}?mock_esign=1"
            }
        
        # TODO: 集成 E签宝 SDK 真实逻辑
        # 1. 获取 AccessToken
        # 2. 上传 PDF 文件获取 FileID
        # 3. 创建签署任务，设置签署区
        # 4. 获取签署链接并返回
        return {"error": "ESIGN_SDK_NOT_IMPLEMENTED"}

    async def check_status(self, flow_id: str):
        """
        查询签署状态
        """
        if self.mock_mode:
            return "SIGNED" # 模拟直接成功
        return "UNKNOWN"

esign_service = ESignService()
