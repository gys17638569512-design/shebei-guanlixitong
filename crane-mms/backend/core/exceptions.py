class BusinessError(Exception):
    """
    业务异常 (对应 HTTP 400)
    """
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)

class UnauthorizedError(Exception):
    """
    未登录或 Token 无效 (对应 HTTP 401)
    """
    def __init__(self, msg: str = "未登录或登录已过期"):
        self.msg = msg
        super().__init__(self.msg)

class ForbiddenError(Exception):
    """
    权限不足 (对应 HTTP 403)
    """
    def __init__(self, msg: str = "权限不足"):
        self.msg = msg
        super().__init__(self.msg)

class NotFoundError(Exception):
    """
    资源不存在 (对应 HTTP 404)
    """
    def __init__(self, msg: str = "资源不存在"):
        self.msg = msg
        super().__init__(self.msg)

class ConflictError(Exception):
    """
    资源冲突/重复操作 (对应 HTTP 409)
    """
    def __init__(self, msg: str = "操作冲突"):
        self.msg = msg
        super().__init__(self.msg)
