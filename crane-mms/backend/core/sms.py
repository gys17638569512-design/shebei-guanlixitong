"""
短信发送服务 (阿里云 SMS)
================================
SMS_MOCK=true  → 仅打印日志，不真实调用 API（开发调试用）
SMS_MOCK=false → 真实调用阿里云短信网关

接入步骤：
1. 登录 https://dysms.console.aliyun.com/
2. 申请短信签名（需营业执照）
3. 申请短信模板（填写模板内容，如：维保工单#{order_id}已派发，请在App中查看）
4. 将 App ID、Secret 和模板 Code 填入 .env 文件
5. 将 SMS_MOCK 改为 false
"""
import logging
from core.settings import settings

logger = logging.getLogger(__name__)


def _send_real(phone: str, template_code: str, params: dict) -> bool:
    """调用阿里云短信 API 真实发送"""
    try:
        from alibabacloud_dysmsapi20170525 import models as sms_models
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_tea_openapi import models as open_api_models
        import json

        config = open_api_models.Config(
            access_key_id=settings.SMS_ACCESS_KEY_ID,
            access_key_secret=settings.SMS_ACCESS_KEY_SECRET,
            endpoint="dysmsapi.aliyuncs.com"
        )
        client = Client(config)
        req = sms_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=settings.SMS_SIGN_NAME,
            template_code=template_code,
            template_param=json.dumps(params, ensure_ascii=False)
        )
        resp = client.send_sms(req)
        if resp.body.code == "OK":
            logger.info(f"[SMS] ✅ 发送成功 → {phone} 模板:{template_code}")
            return True
        else:
            logger.error(f"[SMS] ❌ 发送失败 → {phone} Code:{resp.body.code} Msg:{resp.body.message}")
            return False
    except ImportError:
        logger.error("[SMS] 未安装阿里云 SDK: pip install alibabacloud-dysmsapi20170525")
        return False
    except Exception as e:
        logger.error(f"[SMS] 发送异常: {e}")
        return False


def _send_mock(phone: str, template_code: str, params: dict):
    """模拟发送（仅打印日志）"""
    logger.info(f"[SMS MOCK] 📱 → {phone} 模板:{template_code} 参数:{params}")


def send_sms(phone: str, template_code: str, params: dict) -> bool:
    """主入口：根据配置决定是模拟还是真实发送"""
    if not phone or not template_code:
        return False

    if settings.SMS_MOCK:
        _send_mock(phone, template_code, params)
        return True
    return _send_real(phone, template_code, params)


# ========== 各业务场景封装 ==========

def send_dispatch_sms(phone: str, order_id: int, customer_name: str):
    """工程师收到派单提醒"""
    return send_sms(phone, settings.SMS_TEMPLATE_CODE_DISPATCH or "模板未配置", {
        "order_id": str(order_id),
        "customer": customer_name
    })


def send_sign_request_sms(phone: str, order_id: int, portal_url: str):
    """客户收到签字请求链接"""
    return send_sms(phone, settings.SMS_TEMPLATE_CODE_SIGN or "模板未配置", {
        "order_id": str(order_id),
        "url": f"{settings.CUSTOMER_PORTAL_URL}/sign/{order_id}"
    })


def send_report_ready_sms(phone: str, order_id: int):
    """客户收到报告完成通知"""
    return send_sms(phone, settings.SMS_TEMPLATE_CODE_REPORT or "模板未配置", {
        "order_id": str(order_id),
        "url": f"{settings.CUSTOMER_PORTAL_URL}/orders/{order_id}"
    })


def send_verify_code_sms(phone: str, code: str):
    """客户门户登录验证码"""
    return send_sms(phone, settings.SMS_TEMPLATE_CODE_VERIFY or "模板未配置", {
        "code": code
    })
