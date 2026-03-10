"""
微信服务封装（小程序订阅消息 + 公众号模板消息）
===================================================
WECHAT_MOCK=true  → 仅打印日志，不调用微信 API
WECHAT_MOCK=false → 真实调用微信云服务

接入步骤：
1. 登录 https://mp.weixin.qq.com/ 注册小程序/公众号
2. 获取 AppID 和 AppSecret
3. 小程序订阅消息：在"功能-订阅消息"中申请消息模板
4. 将配置填入 .env 文件
5. 将 WECHAT_MOCK 改为 false
"""
import logging
import requests
from core.settings import settings

logger = logging.getLogger(__name__)

_access_token_cache = {"token": None, "expires_at": 0}


def _get_access_token() -> str | None:
    """获取微信 access_token（带缓存，避免频繁请求）"""
    import time
    now = time.time()
    if _access_token_cache["token"] and _access_token_cache["expires_at"] > now:
        return _access_token_cache["token"]

    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={settings.WECHAT_APP_ID}&secret={settings.WECHAT_APP_SECRET}"
    try:
        res = requests.get(url, timeout=5).json()
        token = res.get("access_token")
        if token:
            _access_token_cache["token"] = token
            _access_token_cache["expires_at"] = now + 7000  # token 有效期 7200s
            return token
        logger.error(f"[WeChat] 获取 access_token 失败: {res}")
    except Exception as e:
        logger.error(f"[WeChat] 网络异常: {e}")
    return None


def send_miniapp_subscribe_message(openid: str, template_id: str, data: dict, page: str = "") -> bool:
    """发送小程序订阅消息"""
    if settings.WECHAT_MOCK:
        logger.info(f"[WeChat MOCK] 📲 订阅消息 → openid:{openid} 模板:{template_id} 数据:{data}")
        return True

    token = _get_access_token()
    if not token:
        return False

    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}"
    payload = {
        "touser": openid,
        "template_id": template_id,
        "page": page,
        "data": {k: {"value": v} for k, v in data.items()}
    }
    try:
        res = requests.post(url, json=payload, timeout=5).json()
        if res.get("errcode") == 0:
            logger.info(f"[WeChat] ✅ 订阅消息发送成功 → {openid}")
            return True
        logger.error(f"[WeChat] 订阅消息失败: {res}")
    except Exception as e:
        logger.error(f"[WeChat] 发送异常: {e}")
    return False


# ========== 各业务场景封装 ==========

def notify_tech_new_order(openid: str, order_id: int, customer_name: str, plan_date: str):
    """通知工程师：新工单已派发"""
    return send_miniapp_subscribe_message(
        openid=openid,
        template_id="YOUR_SUBSCRIBE_TEMPLATE_ID_DISPATCH",  # 在微信后台申请后替换
        data={
            "thing1": f"维保工单 #{order_id}",
            "thing2": customer_name,
            "date3": plan_date
        },
        page=f"pages/orders/detail?id={order_id}"
    )


def notify_tech_order_reminder(openid: str, order_id: int):
    """提醒工程师：工单即将到期"""
    return send_miniapp_subscribe_message(
        openid=openid,
        template_id="YOUR_SUBSCRIBE_TEMPLATE_ID_REMINDER",
        data={"thing1": f"工单 #{order_id} 计划维保日期临近，请及时处理"}
    )
