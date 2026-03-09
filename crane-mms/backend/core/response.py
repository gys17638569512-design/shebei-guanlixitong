from typing import Any, Optional

def ok(data: Any = None, msg: str = "success") -> dict:
    """
    统一成功响应格式
    """
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }

def err(code: int, msg: str, data: Any = None) -> dict:
    """
    统一错误响应格式
    """
    return {
        "code": code,
        "msg": msg,
        "data": data
    }
