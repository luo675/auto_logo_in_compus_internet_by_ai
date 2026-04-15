#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常类
定义项目特定的异常类型
"""


class CampusAutoLoginError(Exception):
    """校园网自动登录工具的基础异常类"""
    pass


class ConfigError(CampusAutoLoginError):
    """配置相关错误"""
    pass


class NetworkError(CampusAutoLoginError):
    """网络相关错误"""
    pass


class ConnectionError(NetworkError):
    """连接错误"""
    pass


class TimeoutError(CampusAutoLoginError):
    """超时错误"""
    pass


class AuthenticationError(CampusAutoLoginError):
    """认证错误"""
    pass


class BrowserError(CampusAutoLoginError):
    """浏览器相关错误"""
    pass


class ProcessError(CampusAutoLoginError):
    """进程相关错误"""
    pass


class RepairError(CampusAutoLoginError):
    """修复工具错误"""
    pass


class AutomationError(CampusAutoLoginError):
    """自动化操作错误"""
    pass


class WindowNotFoundError(AutomationError):
    """窗口未找到错误"""
    pass


class ControlNotFoundError(AutomationError):
    """控件未找到错误"""
    pass


class LoginFailedError(AuthenticationError):
    """登录失败错误"""
    pass


class DependencyError(CampusAutoLoginError):
    """依赖库错误"""
    pass


class ValidationError(CampusAutoLoginError):
    """验证错误"""
    pass


def handle_exception(func):
    """
    异常处理装饰器
    
    捕获异常并记录日志，然后重新抛出
    """
    import functools
    import logging
    
    logger = logging.getLogger(__name__)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CampusAutoLoginError:
            raise  # 重新抛出项目特定的异常
        except Exception as e:
            logger.error(f"未处理的异常 in {func.__name__}: {e}")
            raise CampusAutoLoginError(f"执行 {func.__name__} 时发生错误: {e}") from e
    
    return wrapper


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        delay: 重试延迟（秒）
        exceptions: 触发重试的异常类型
    """
    import functools
    import time
    import logging
    
    logger = logging.getLogger(__name__)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} 第{attempt}次失败: {e}，"
                            f"{delay}秒后重试"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} 所有{max_attempts}次尝试均失败"
                        )
                        raise
            
            # 理论上不会执行到这里
            raise CampusAutoLoginError(f"{func.__name__} 重试失败")
        
        return wrapper
    return decorator