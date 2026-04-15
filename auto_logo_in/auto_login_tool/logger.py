#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志和通知模块
提供统一的日志记录和Windows通知功能
"""

import os
import sys
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


class LoggerNotifier:
    """日志通知器类"""
    
    def __init__(self, config_manager=None, log_dir: str = "logs"):
        """
        初始化日志通知器
        
        Args:
            config_manager: 配置管理器实例
            log_dir: 日志目录
        """
        self.config = config_manager
        self.log_dir = Path(log_dir)
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 初始化通知器
        self.notifier = None
        self.enable_notifications = True
        
        # 加载配置
        self._load_config()
        
        # 设置日志
        self._setup_logging()
        
        # 初始化Windows通知
        self._init_notifications()
    
    def _load_config(self):
        """从配置加载设置"""
        if self.config:
            log_level_str = self.config.get('settings', 'log_level', 'INFO')
            self.enable_notifications = self.config.get('settings', 'enable_notifications', True)
        else:
            log_level_str = 'INFO'
            self.enable_notifications = True
        
        # 转换日志级别
        self.log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        
        # 日志文件路径
        today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = self.log_dir / f'campus_auto_login_{today}.log'
    
    def _setup_logging(self):
        """设置日志系统"""
        # 创建logger
        self.logger = logging.getLogger('CampusAutoLogin')
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
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            rotate_handler.setLevel(self.log_level)
            rotate_handler.setFormatter(formatter)
            self.logger.addHandler(rotate_handler)
        except Exception as e:
            self.logger.warning(f"无法创建旋转日志文件handler: {e}")
        
        self.logger.info(f"日志系统初始化完成，日志级别: {logging.getLevelName(self.log_level)}")
        self.logger.info(f"日志文件: {self.log_file}")
    
    def _init_notifications(self):
        """初始化通知系统"""
        if TOAST_AVAILABLE and self.enable_notifications:
            try:
                self.notifier = ToastNotifier()
                self.logger.debug("Windows通知系统初始化成功")
            except Exception as e:
                self.logger.warning(f"初始化Windows通知系统失败: {e}")
                self.notifier = None
        else:
            if not TOAST_AVAILABLE:
                self.logger.debug("win10toast库未安装，Windows通知不可用")
            if not self.enable_notifications:
                self.logger.debug("通知功能已禁用")
            self.notifier = None
    
    def log(self, level: str, message: str, **kwargs):
        """
        记录日志
        
        Args:
            level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
            message: 日志消息
            **kwargs: 额外参数
        """
        level = level.lower()
        
        if level == 'debug':
            self.logger.debug(message, **kwargs)
        elif level == 'info':
            self.logger.info(message, **kwargs)
        elif level == 'warning':
            self.logger.warning(message, **kwargs)
        elif level == 'error':
            self.logger.error(message, **kwargs)
        elif level == 'critical':
            self.logger.critical(message, **kwargs)
        else:
            self.logger.info(message, **kwargs)
    
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
    
    def notify_user(self, title: str, message: str, duration: int = 5, 
                   icon_path: Optional[str] = None) -> bool:
        """
        发送Windows通知
        
        Args:
            title: 通知标题
            message: 通知内容
            duration: 显示时长（秒）
            icon_path: 图标路径
            
        Returns:
            bool: 是否成功发送
        """
        if not self.enable_notifications:
            self.debug(f"通知功能已禁用，跳过通知: {title} - {message}")
            return False
        
        if not self.notifier:
            self.debug(f"通知系统不可用，跳过通知: {title} - {message}")
            return False
        
        try:
            self.notifier.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon_path,
                threaded=True
            )
            self.info(f"已发送通知: {title} - {message}")
            return True
        except Exception as e:
            self.error(f"发送通知失败: {e}")
            return False
    
    def send_error_alert(self, error: Exception or str, context: str = ""):
        """
        发送错误警报
        
        Args:
            error: 错误对象或错误消息
            context: 错误上下文
        """
        if isinstance(error, Exception):
            error_msg = f"{type(error).__name__}: {str(error)}"
        else:
            error_msg = str(error)
        
        # 记录错误日志
        full_message = f"{context}: {error_msg}" if context else error_msg
        self.error(full_message)
        
        # 发送通知
        title = "校园网自动登录工具 - 错误"
        message = f"{context}\n{error_msg}" if context else error_msg
        
        # 截断过长的消息
        if len(message) > 200:
            message = message[:197] + "..."
        
        self.notify_user(title, message, duration=10)
    
    def send_success_notification(self, operation: str, details: str = ""):
        """
        发送成功通知
        
        Args:
            operation: 操作名称
            details: 详细信息
        """
        title = "校园网自动登录工具 - 成功"
        message = f"{operation} 成功"
        if details:
            message += f"\n{details}"
        
        self.info(f"{operation} 成功: {details}")
        self.notify_user(title, message)
    
    def send_warning_notification(self, warning: str, details: str = ""):
        """
        发送警告通知
        
        Args:
            warning: 警告内容
            details: 详细信息
        """
        title = "校园网自动登录工具 - 警告"
        message = warning
        if details:
            message += f"\n{details}"
        
        self.warning(f"{warning}: {details}")
        self.notify_user(title, message, duration=8)
    
    def log_operation_start(self, operation: str, details: Dict[str, Any] = None):
        """
        记录操作开始
        
        Args:
            operation: 操作名称
            details: 操作详情
        """
        message = f"开始 {operation}"
        if details:
            details_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({details_str})"
        
        self.info(message)
    
    def log_operation_end(self, operation: str, success: bool, 
                         details: Dict[str, Any] = None):
        """
        记录操作结束
        
        Args:
            operation: 操作名称
            success: 是否成功
            details: 操作详情
        """
        status = "成功" if success else "失败"
        message = f"结束 {operation} - {status}"
        
        if details:
            details_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({details_str})"
        
        if success:
            self.info(message)
        else:
            self.warning(message)
    
    def get_log_file_path(self) -> Path:
        """
        获取当前日志文件路径
        
        Returns:
            Path: 日志文件路径
        """
        return self.log_file
    
    def get_recent_logs(self, lines: int = 50) -> str:
        """
        获取最近的日志
        
        Args:
            lines: 要获取的行数
            
        Returns:
            str: 最近的日志内容
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
        except Exception as e:
            return f"无法读取日志文件: {e}"
    
    def clear_old_logs(self, days_to_keep: int = 7):
        """
        清理旧日志文件
        
        Args:
            days_to_keep: 保留多少天的日志
        """
        import time
        from datetime import datetime, timedelta
        
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob('campus_auto_login_*.log'):
                if log_file.is_file():
                    file_time = log_file.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            log_file.unlink()
                            self.info(f"已删除旧日志文件: {log_file.name}")
                        except Exception as e:
                            self.warning(f"删除日志文件失败 {log_file.name}: {e}")
        except Exception as e:
            self.error(f"清理旧日志时出错: {e}")


# 单例实例
_logger_instance = None

def get_logger_notifier(config_manager=None, log_dir: str = "logs") -> LoggerNotifier:
    """
    获取日志通知器单例
    
    Args:
        config_manager: 配置管理器实例
        log_dir: 日志目录
        
    Returns:
        LoggerNotifier实例
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LoggerNotifier(config_manager, log_dir)
    return _logger_instance


# 测试函数
def test_logger_notifier():
    """测试日志通知器"""
    logger = get_logger_notifier()
    
    print("=== 日志通知器测试 ===")
    
    # 测试各种日志级别
    print("\n1. 测试日志级别:")
    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    
    # 测试通知
    print("\n2. 测试通知（如果可用）:")
    success = logger.notify_user("测试通知", "这是一条测试通知", duration=3)
    print(f"   通知发送成功: {success}")
    
    # 测试错误警报
    print("\n3. 测试错误警报:")
    try:
        raise ValueError("测试错误")
    except ValueError as e:
        logger.send_error_alert(e, "测试错误警报")
    
    # 测试成功通知
    print("\n4. 测试成功通知:")
    logger.send_success_notification("测试操作", "详细信息")
    
    # 测试操作日志
    print("\n5. 测试操作日志:")
    logger.log_operation_start("测试操作", {"param1": "value1", "param2": 123})
    logger.log_operation_end("测试操作", True, {"result": "success", "time": "5s"})
    
    # 显示日志文件路径
    print(f"\n6. 日志文件: {logger.get_log_file_path()}")
    
    # 显示最近日志
    print("\n7. 最近日志:")
    recent_logs = logger.get_recent_logs(10)
    print(recent_logs)


if __name__ == "__main__":
    test_logger_notifier()