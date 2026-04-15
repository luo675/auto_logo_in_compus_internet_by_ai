#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化日志记录工具
提供统一的日志记录和Windows通知功能
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 尝试导入Windows通知库
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False


class SimpleLogger:
    """
    简化日志记录器
    
    替代原有的复杂LoggerNotifier，提供基本功能：
    - 控制台和文件日志
    - Windows通知（可选）
    - 操作开始/结束记录
    """
    
    def __init__(
        self,
        name: str = "CampusAutoLogin",
        log_dir: str = "logs",
        log_level: str = "INFO",
        enable_notifications: bool = True
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志器名称
            log_dir: 日志目录
            log_level: 日志级别
            enable_notifications: 是否启用Windows通知
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.enable_notifications = enable_notifications
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志文件路径
        today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = self.log_dir / f'campus_auto_login_{today}.log'
        
        # 初始化通知器
        self.notifier = None
        self._init_notifications()
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志系统"""
        # 创建logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # 清除已有的handler，避免重复
        self.logger.handlers.clear()
        
        # 创建formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # 添加一个旋转文件handler，防止日志过大
        try:
            rotate_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            rotate_handler.setLevel(self.log_level)
            rotate_handler.setFormatter(formatter)
            self.logger.addHandler(rotate_handler)
        except Exception as e:
            self.logger.warning(f"无法创建旋转文件handler: {e}")
    
    def _init_notifications(self):
        """初始化通知系统"""
        if not self.enable_notifications or not TOAST_AVAILABLE:
            self.notifier = None
            return
        
        try:
            self.notifier = ToastNotifier()
        except Exception as e:
            self.warning(f"初始化Windows通知失败: {e}")
            self.notifier = None
    
    def log(self, level: str, message: str, **kwargs):
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外参数
        """
        extra = kwargs.copy()
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, extra=extra if extra else None)
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.log('debug', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.log('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.log('critical', message, **kwargs)
    
    def send_notification(self, title: str, message: str, duration: int = 5):
        """
        发送Windows通知
        
        Args:
            title: 通知标题
            message: 通知内容
            duration: 显示时长（秒）
        """
        if not self.enable_notifications or not self.notifier:
            return
        
        try:
            self.notifier.show_toast(
                title=title,
                msg=message,
                duration=duration,
                threaded=True
            )
        except Exception as e:
            self.warning(f"发送通知失败: {e}")
    
    def send_success_notification(self, operation: str, details: str = ""):
        """
        发送成功通知
        
        Args:
            operation: 操作名称
            details: 详细信息
        """
        title = f"{operation} - 成功"
        message = f"{operation} 已完成"
        if details:
            message += f": {details}"
        
        self.info(f"{operation} 成功: {details}")
        self.send_notification(title, message)
    
    def send_warning_notification(self, warning: str, details: str = ""):
        """
        发送警告通知
        
        Args:
            warning: 警告内容
            details: 详细信息
        """
        title = f"警告: {warning}"
        message = details if details else warning
        
        self.warning(f"{warning}: {details}")
        self.send_notification(title, message)
    
    def send_error_alert(self, error: Exception or str, context: str = ""):
        """
        发送错误警报
        
        Args:
            error: 错误对象或字符串
            context: 错误上下文
        """
        if isinstance(error, Exception):
            error_msg = str(error)
            error_type = error.__class__.__name__
        else:
            error_msg = error
            error_type = "Error"
        
        title = f"错误: {error_type}"
        message = error_msg
        if context:
            message = f"{context}: {error_msg}"
        
        self.error(f"{context}: {error_msg}")
        self.send_notification(title, message)
    
    def log_operation_start(self, operation: str, details: Dict[str, Any] = None):
        """
        记录操作开始
        
        Args:
            operation: 操作名称
            details: 操作详情
        """
        message = f"开始 {operation}"
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({detail_str})"
        
        self.info(message)
    
    def log_operation_end(
        self,
        operation: str,
        success: bool,
        details: Dict[str, Any] = None
    ):
        """
        记录操作结束
        
        Args:
            operation: 操作名称
            success: 是否成功
            details: 操作详情
        """
        status = "成功" if success else "失败"
        message = f"{operation} {status}"
        
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({detail_str})"
        
        if success:
            self.info(message)
        else:
            self.warning(message)
    
    def clear_old_logs(self, days_to_keep: int = 7):
        """
        清理旧日志文件
        
        Args:
            days_to_keep: 保留天数
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"已删除旧日志文件: {log_file}")
        except Exception as e:
            self.warning(f"清理旧日志失败: {e}")


# 全局日志记录器实例
_logger_instance: Optional[SimpleLogger] = None


def get_logger(
    name: str = "CampusAutoLogin",
    log_dir: str = "logs",
    log_level: str = "INFO",
    enable_notifications: bool = True
) -> SimpleLogger:
    """
    获取日志记录器实例（单例模式）
    
    Args:
        name: 日志器名称
        log_dir: 日志目录
        log_level: 日志级别
        enable_notifications: 是否启用通知
    
    Returns:
        SimpleLogger: 日志记录器实例
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = SimpleLogger(
            name=name,
            log_dir=log_dir,
            log_level=log_level,
            enable_notifications=enable_notifications
        )
    
    return _logger_instance


def get_logger_from_config(config) -> SimpleLogger:
    """
    从配置获取日志记录器
    
    Args:
        config: 配置管理器实例
    
    Returns:
        SimpleLogger: 日志记录器实例
    """
    log_level = config.get('settings', 'log_level', 'INFO')
    enable_notifications = config.get('settings', 'enable_notifications', True)
    
    return get_logger(
        name="CampusAutoLogin",
        log_dir="logs",
        log_level=log_level,
        enable_notifications=enable_notifications
    )