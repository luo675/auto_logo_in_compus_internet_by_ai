#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能等待工具模块
提供更灵活的等待机制，替代硬编码的 time.sleep()
"""

import time
import logging
from typing import Callable, Optional, Any, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


def wait_until(
    condition: Callable[[], Tuple[bool, Any]],
    timeout: float = 30.0,
    interval: float = 1.0,
    description: str = "等待条件满足"
) -> Tuple[bool, Any]:
    """
    等待直到条件满足或超时
    
    Args:
        condition: 返回 (是否满足, 额外数据) 的可调用对象
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        description: 等待描述，用于日志
    
    Returns:
        Tuple[bool, Any]: (是否成功, 条件返回的额外数据)
    """
    start_time = time.time()
    last_log_time = start_time
    
    while True:
        success, data = condition()
        
        if success:
            elapsed = time.time() - start_time
            logger.debug(f"{description} 成功，耗时 {elapsed:.2f}秒")
            return True, data
        
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            logger.warning(f"{description} 超时（{timeout}秒）")
            return False, data
        
        # 每5秒记录一次等待状态
        if time.time() - last_log_time >= 5.0:
            logger.debug(f"{description} 中... 已等待 {elapsed:.1f}秒")
            last_log_time = time.time()
        
        time.sleep(min(interval, timeout - elapsed))


def wait_for_process(
    process_checker: Callable[[], bool],
    process_name: str,
    timeout: float = 30.0,
    interval: float = 1.0
) -> bool:
    """
    等待进程出现或消失
    
    Args:
        process_checker: 返回True表示进程存在
        process_name: 进程名称（用于日志）
        timeout: 超时时间
        interval: 检查间隔
    
    Returns:
        bool: 是否在超时前满足条件
    """
    def condition():
        exists = process_checker()
        return exists, exists
    
    success, _ = wait_until(
        condition,
        timeout=timeout,
        interval=interval,
        description=f"等待进程 {process_name}"
    )
    return success


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器，在失败时自动重试
    
    Args:
        max_attempts: 最大尝试次数
        delay: 初始延迟（秒）
        backoff_factor: 退避因子，每次重试延迟乘以该因子
        exceptions: 触发重试的异常类型
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.debug(f"尝试执行 {func.__name__} (第{attempt}次)")
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} 第{attempt}次失败: {e}，"
                            f"{current_delay}秒后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} 所有{max_attempts}次尝试均失败"
                        )
            
            # 所有尝试都失败，重新抛出最后一个异常
            raise last_exception
        
        return wrapper
    return decorator


class TimeoutError(Exception):
    """自定义超时异常"""
    pass


def timeout(
    seconds: float,
    error_message: str = "操作超时"
):
    """
    超时装饰器，限制函数执行时间
    
    Args:
        seconds: 超时时间（秒）
        error_message: 超时时的错误消息
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import threading
            
            result = []
            exception = []
            
            def target():
                try:
                    result.append(func(*args, **kwargs))
                except Exception as e:
                    exception.append(e)
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                logger.error(f"{func.__name__} {error_message}")
                raise TimeoutError(error_message)
            
            if exception:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator


def exponential_backoff(
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0
):
    """
    指数退避生成器
    
    Args:
        initial_delay: 初始延迟
        max_delay: 最大延迟
        factor: 增长因子
    
    Yields:
        每次重试的延迟时间
    """
    delay = initial_delay
    while True:
        yield delay
        delay = min(delay * factor, max_delay)


# 兼容性函数，用于逐步替换现有的 time.sleep() 调用
def smart_sleep(
    seconds: float,
    check_interrupt: Optional[Callable[[], bool]] = None,
    interrupt_interval: float = 1.0
) -> bool:
    """
    智能睡眠，可以中断
    
    Args:
        seconds: 需要睡眠的总时间
        check_interrupt: 中断检查函数，返回True时中断睡眠
        interrupt_interval: 中断检查间隔
    
    Returns:
        bool: 是否被中断
    """
    if check_interrupt is None:
        time.sleep(seconds)
        return False
    
    start_time = time.time()
    while time.time() - start_time < seconds:
        if check_interrupt():
            elapsed = time.time() - start_time
            logger.debug(f"睡眠被中断，实际睡眠 {elapsed:.2f}秒")
            return True
        time.sleep(min(interrupt_interval, seconds - (time.time() - start_time)))
    
    return False