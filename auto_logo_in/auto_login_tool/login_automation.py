#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Dr.COM客户端自动化模块
启动Dr.COM客户端，检测登录状态，模拟GUI操作输入账号密码
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 导入工具模块
from .utils.wait import wait_until, retry_on_failure
from .utils.exceptions import (
    AutomationError, WindowNotFoundError, ControlNotFoundError,
    LoginFailedError, handle_exception
)

# 尝试导入GUI自动化库
try:
    import pywinauto
    from pywinauto import Application, findwindows
    from pywinauto.keyboard import send_keys
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logging.warning("pywinauto库未安装，Dr.COM自动化功能受限")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("pyautogui库未安装，备用自动化功能受限")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil库未安装，进程管理功能受限")


class DrComAutomator:
    """Dr.COM客户端自动化器类（简化版）"""
    
    def __init__(self, config_manager=None):
        """
        初始化Dr.COM自动化器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Dr.COM客户端相关信息
        self.client_name = "Dr.COM宽带认证客户端"
        self.process_names = ["DrClient.exe", "DrMain.exe", "DrUpdate.exe"]
        
        # 窗口标题关键词
        self.window_titles = [
            "网络选择",
            "Dr.COM 宽带认证客户端",
            "Dr.COM宽带认证客户端",
            "Dr.COM",
            "宽带认证客户端",
            "DrClient",
            "DrMain",
            "DrUpdate",
        ]
        
        # 加载配置
        self._load_config()
        
        # 应用程序连接
        self.app = None
        self.window = None
    
    def _load_config(self):
        """从配置加载设置"""
        if self.config:
            self.drcom_path = Path(self.config.get('paths', 'drcom_path', 
                                                 r'C:\Users\luo\Desktop\APP\DrClient.exe'))
            self.retry_count = self.config.get('settings', 'retry_count', 3)
            self.retry_interval = self.config.get('settings', 'retry_interval', 10)
        else:
            self.drcom_path = Path(r'C:\Users\luo\Desktop\APP\DrClient.exe')
            self.retry_count = 3
            self.retry_interval = 10
        
        self.logger.debug(f"Dr.COM路径: {self.drcom_path}")
        self.logger.debug(f"重试次数: {self.retry_count}, 重试间隔: {self.retry_interval}")
    
    @handle_exception
    def is_client_running(self) -> bool:
        """
        检查Dr.COM客户端是否在运行
        
        Returns:
            bool: 是否在运行
        """
        # 使用psutil检查进程
        if PSUTIL_AVAILABLE:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and any(
                        target_name.lower() in proc_name.lower() 
                        for target_name in self.process_names
                    ):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # 使用pywinauto检查窗口
        if PYWINAUTO_AVAILABLE:
            try:
                windows = findwindows.find_windows(
                    title_re=".*Dr.*|.*COM.*|.*宽带.*|.*认证.*"
                )
                return len(windows) > 0
            except Exception:
                pass
        
        return False
    
    @handle_exception
    def find_client_window(self) -> Optional[any]:
        """
        查找Dr.COM客户端窗口
        
        Returns:
            Optional[any]: 窗口对象，未找到返回None
        """
        if not PYWINAUTO_AVAILABLE:
            return None
        
        # 尝试多种连接方法
        connection_methods = [
            self._connect_by_title,
            self._connect_by_process,
            self._connect_by_windows_api,
        ]
        
        for method in connection_methods:
            try:
                if method():
                    self.window = self.app.window()
                    if self.window.exists():
                        self.logger.info(f"找到Dr.COM窗口: {self.window.window_text()}")
                        return self.window
            except Exception as e:
                self.logger.debug(f"连接方法失败: {e}")
                continue
        
        self.logger.warning("未找到Dr.COM窗口")
        return None
    
    def _connect_by_title(self) -> bool:
        """通过窗口标题连接"""
        for title in self.window_titles:
            try:
                self.app = Application().connect(title=title)
                self.logger.debug(f"通过标题连接到Dr.COM客户端: {title}")
                return True
            except Exception:
                continue
        return False
    
    def _connect_by_process(self) -> bool:
        """通过进程名连接"""
        for process_name in self.process_names:
            try:
                self.app = Application().connect(process=process_name)
                self.logger.debug(f"通过进程连接到Dr.COM客户端: {process_name}")
                return True
            except Exception:
                continue
        return False
    
    def _connect_by_windows_api(self) -> bool:
        """通过Windows API连接"""
        try:
            import ctypes
            from ctypes import wintypes
            
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(
                wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
            )
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            
            def foreach_window(hwnd, lParam):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                if buff.value and any(
                    keyword in buff.value 
                    for keyword in ['Dr', 'COM', '宽带', '认证']
                ):
                    try:
                        self.app = Application().connect(handle=hwnd)
                        self.logger.debug(f"通过Windows API连接到Dr.COM客户端: {buff.value}")
                        return False  # 停止枚举
                    except Exception:
                        pass
                return True  # 继续枚举
            
            EnumWindows(EnumWindowsProc(foreach_window), 0)
            return self.app is not None
            
        except Exception as e:
            self.logger.debug(f"Windows API连接失败: {e}")
            return False
    
    @handle_exception
    def start_client(self) -> bool:
        """
        启动Dr.COM客户端
        
        Returns:
            bool: 是否成功启动
        """
        if self.is_client_running():
            self.logger.info("Dr.COM客户端已在运行")
            return True
        
        if not self.drcom_path.exists():
            self.logger.error(f"Dr.COM客户端路径不存在: {self.drcom_path}")
            return False
        
        try:
            self.logger.info(f"启动Dr.COM客户端: {self.drcom_path}")
            subprocess.Popen([str(self.drcom_path)])
            
            # 等待客户端启动
            def check_client():
                return self.is_client_running(), None
            
            success, _ = wait_until(
                check_client,
                timeout=30,
                interval=2,
                description="等待Dr.COM客户端启动"
            )
            
            if success:
                self.logger.info("Dr.COM客户端启动成功")
                return True
            else:
                self.logger.warning("Dr.COM客户端启动超时")
                return False
                
        except Exception as e:
            self.logger.error(f"启动Dr.COM客户端失败: {e}")
            return False
    
    @handle_exception
    def is_logged_in(self) -> Tuple[bool, str]:
        """
        检查是否已登录
        
        Returns:
            Tuple[bool, str]: (是否已登录, 状态消息)
        """
        window = self.find_client_window()
        if not window:
            return False, "未找到Dr.COM窗口"
        
        try:
            # 尝试查找状态文本控件
            window_text = window.window_text()
            
            # 根据窗口文本判断状态
            if "已连接" in window_text or "已登录" in window_text or "在线" in window_text:
                return True, "已登录"
            elif "未连接" in window_text or "未登录" in window_text or "离线" in window_text:
                return False, "未登录"
            else:
                # 默认认为未登录
                return False, "状态未知"
                
        except Exception as e:
            self.logger.debug(f"检查登录状态时出错: {e}")
            return False, f"检查状态时出错: {e}"
    
    @retry_on_failure(max_attempts=3, delay=2.0)
    @handle_exception
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            Tuple[bool, str]: (是否成功, 状态消息)
        """
        self.logger.info(f"尝试登录，用户名: {username}")
        
        # 确保客户端在运行
        if not self.start_client():
            return False, "无法启动Dr.COM客户端"
        
        # 查找窗口
        window = self.find_client_window()
        if not window:
            return False, "未找到Dr.COM窗口"
        
        try:
            # 激活窗口
            window.set_focus()
            time.sleep(1)
            
            # 尝试自动查找控件并输入
            success, message = self._auto_find_and_input(window, username, password)
            if success:
                return True, message
            
            # 如果自动查找失败，使用备用方法
            self.logger.info("自动查找控件失败，使用备用方法")
            return self._fallback_login_method(window, username, password)
            
        except Exception as e:
            self.logger.error(f"登录过程中出错: {e}")
            return False, f"登录过程中出错: {e}"
    
    def _auto_find_and_input(self, window, username: str, password: str) -> Tuple[bool, str]:
        """自动查找控件并输入"""
        try:
            # 查找用户名输入框
            username_controls = window.descendants(
                control_type="Edit",
                title=""
            )
            
            if username_controls:
                username_ctrl = username_controls[0]
                username_ctrl.set_focus()
                username_ctrl.set_text(username)
                self.logger.debug("已输入用户名")
            else:
                # 使用键盘模拟
                window.set_focus()
                pyautogui.write(username)
                self.logger.debug("使用键盘模拟输入用户名")
            
            # 切换到密码框（按Tab键）
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # 输入密码
            pyautogui.write(password)
            self.logger.debug("已输入密码")
            
            # 按回车登录
            pyautogui.press('enter')
            self.logger.debug("已按回车键")
            
            # 等待登录结果
            time.sleep(3)
            
            # 检查是否登录成功
            logged_in, status_msg = self.is_logged_in()
            if logged_in:
                return True, "登录成功"
            else:
                return False, f"登录失败: {status_msg}"
                
        except Exception as e:
            self.logger.debug(f"自动查找控件失败: {e}")
            return False, f"自动查找控件失败: {e}"
    
    def _fallback_login_method(self, window, username: str, password: str) -> Tuple[bool, str]:
        """备用登录方法"""
        try:
            # 简单方法：直接使用键盘输入
            window.set_focus()
            time.sleep(1)
            
            # 输入用户名
            pyautogui.write(username)
            time.sleep(0.5)
            
            # 切换到密码框
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # 输入密码
            pyautogui.write(password)
            time.sleep(0.5)
            
            # 按回车登录
            pyautogui.press('enter')
            time.sleep(3)
            
            # 检查登录结果
            logged_in, status_msg = self.is_logged_in()
            if logged_in:
                return True, "登录成功（使用备用方法）"
            else:
                return False, f"登录失败（备用方法）: {status_msg}"
                
        except Exception as e:
            self.logger.error(f"备用登录方法失败: {e}")
            return False, f"备用登录方法失败: {e}"
    
    @handle_exception
    def login_with_retry(self, username: str, password: str) -> Tuple[bool, str, int]:
        """
        带重试的登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            Tuple[bool, str, int]: (是否成功, 状态消息, 尝试次数)
        """
        attempts = 0
        max_attempts = self.retry_count
        
        for attempt in range(1, max_attempts + 1):
            attempts = attempt
            self.logger.info(f"登录尝试第{attempt}次")
            
            success, message = self.login(username, password)
            
            if success:
                return True, message, attempts
            
            self.logger.warning(f"第{attempt}次登录失败: {message}")
            
            if attempt < max_attempts:
                self.logger.info(f"{self.retry_interval}秒后重试...")
                time.sleep(self.retry_interval)
        
        return False, f"所有{max_attempts}次登录尝试均失败", attempts


# 测试函数
def test_drcom_automator():
    """测试Dr.COM自动化器"""
    print("测试Dr.COM自动化器...")
    
    # 创建配置管理器
    from config import ConfigManager
    config = ConfigManager()
    
    # 创建自动化器
    automator = DrComAutomator(config)
    
    # 测试客户端是否在运行
    running = automator.is_client_running()
    print(f"客户端是否在运行: {running}")
    
    # 测试查找窗口
    window = automator.find_client_window()
    print(f"找到窗口: {window is not None}")
    
    # 测试登录状态检查
    if window:
        logged_in, status = automator.is_logged_in()
        print(f"登录状态: {logged_in}, 消息: {status}")
    
    print("测试完成")


if __name__ == "__main__":
    test_drcom_automator()