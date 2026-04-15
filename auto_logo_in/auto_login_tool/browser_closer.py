#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版网页关闭模块
自动检测并关闭校园网登录网页
支持多种浏览器：Chrome, Edge, Firefox, IE
"""

import os
import sys
import time
import logging
import subprocess
from typing import List, Optional, Tuple
from pathlib import Path

# 导入工具模块
from .utils.wait import wait_until
from .utils.exceptions import BrowserError, handle_exception

# 尝试导入GUI自动化库
try:
    import pywinauto
    from pywinauto import Application, findwindows
    from pywinauto.keyboard import send_keys
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logging.warning("pywinauto库未安装，网页关闭功能受限")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil库未安装，进程管理功能受限")


class BrowserCloser:
    """浏览器关闭器类（简化版）"""
    
    def __init__(self, config_manager=None):
        """
        初始化浏览器关闭器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 浏览器进程名
        self.browser_processes = {
            'chrome': ['chrome.exe', 'chromium.exe'],
            'edge': ['msedge.exe', 'edge.exe'],
            'firefox': ['firefox.exe'],
            'ie': ['iexplore.exe'],
            'opera': ['opera.exe'],
            'brave': ['brave.exe'],
        }
        
        # 默认关键词
        self.default_keywords = ['校园网', '登录', 'Dr.COM', '认证', '校园网络', '上网认证']
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """从配置加载设置"""
        if self.config:
            keywords_str = self.config.get('browser', 'browser_keywords', '')
            if keywords_str:
                self.keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            else:
                self.keywords = self.default_keywords
                
            self.close_method = self.config.get('browser', 'close_method', 'alt_f4')
            self.close_delay = self.config.get('browser', 'close_delay', 2)
        else:
            self.keywords = self.default_keywords
            self.close_method = 'alt_f4'
            self.close_delay = 2
        
        self.logger.debug(f"浏览器关键词: {self.keywords}")
        self.logger.debug(f"关闭方法: {self.close_method}")
    
    @handle_exception
    def is_browser_open(self) -> bool:
        """
        检查是否有浏览器窗口打开
        
        Returns:
            bool: 是否有浏览器窗口打开
        """
        # 检查进程
        if PSUTIL_AVAILABLE:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name:
                        for browser_names in self.browser_processes.values():
                            if any(
                                browser_name.lower() == proc_name.lower()
                                for browser_name in browser_names
                            ):
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # 检查窗口
        if PYWINAUTO_AVAILABLE:
            try:
                windows = self.find_browser_windows()
                return len(windows) > 0
            except Exception:
                pass
        
        return False
    
    @handle_exception
    def find_browser_windows(self) -> List[Tuple[str, int, str]]:
        """
        查找包含校园网登录关键词的浏览器窗口
        
        Returns:
            List[Tuple[str, int, str]]: 列表元素为(窗口标题, 进程ID, 浏览器类型)
        """
        if not PYWINAUTO_AVAILABLE:
            self.logger.warning("pywinauto不可用，无法查找浏览器窗口")
            return []
        
        windows = []
        
        try:
            # 获取所有可见窗口
            all_windows = findwindows.find_windows(visible_only=True)
            
            for handle in all_windows:
                try:
                    window = findwindows.find_element(handle=handle)
                    title = window.window_text()
                    
                    if not title:
                        continue
                    
                    # 检查是否包含关键词
                    if any(keyword in title for keyword in self.keywords):
                        # 获取进程ID
                        pid = window.process_id()
                        
                        # 确定浏览器类型
                        browser_type = self._get_browser_type(pid)
                        
                        windows.append((title, pid, browser_type))
                        
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"查找浏览器窗口时出错: {e}")
        
        return windows
    
    def _get_browser_type(self, pid: int) -> str:
        """
        根据进程ID确定浏览器类型
        
        Args:
            pid: 进程ID
        
        Returns:
            str: 浏览器类型
        """
        if not PSUTIL_AVAILABLE:
            return "unknown"
        
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name().lower()
            
            for browser_type, browser_names in self.browser_processes.items():
                if any(browser_name.lower() in proc_name for browser_name in browser_names):
                    return browser_type
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return "unknown"
    
    @handle_exception
    def close_browser_windows(self) -> int:
        """
        关闭校园网登录网页
        
        Returns:
            int: 关闭的窗口数量
        """
        windows = self.find_browser_windows()
        
        if not windows:
            self.logger.info("未找到需要关闭的浏览器窗口")
            return 0
        
        self.logger.info(f"找到 {len(windows)} 个需要关闭的浏览器窗口")
        
        closed_count = 0
        
        for title, pid, browser_type in windows:
            try:
                self.logger.debug(f"关闭窗口: {title} (PID: {pid}, 浏览器: {browser_type})")
                
                if self.close_method == 'alt_f4':
                    success = self._close_with_alt_f4(pid)
                elif self.close_method == 'taskkill':
                    success = self._close_with_taskkill(pid)
                else:
                    success = self._close_with_pywinauto(pid)
                
                if success:
                    closed_count += 1
                    self.logger.debug(f"窗口关闭成功: {title}")
                    
                    # 短暂延迟，避免过快关闭多个窗口
                    time.sleep(self.close_delay)
                    
            except Exception as e:
                self.logger.warning(f"关闭窗口失败 {title}: {e}")
        
        return closed_count
    
    def _close_with_alt_f4(self, pid: int) -> bool:
        """使用Alt+F4关闭窗口"""
        if not PYWINAUTO_AVAILABLE:
            return False
        
        try:
            # 连接到进程
            app = Application().connect(process=pid)
            window = app.window()
            
            # 激活窗口
            window.set_focus()
            time.sleep(0.5)
            
            # 发送Alt+F4
            send_keys('%{F4}')
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Alt+F4关闭失败: {e}")
            return False
    
    def _close_with_taskkill(self, pid: int) -> bool:
        """使用taskkill命令终止进程"""
        try:
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          timeout=5)
            return True
        except Exception as e:
            self.logger.debug(f"taskkill关闭失败: {e}")
            return False
    
    def _close_with_pywinauto(self, pid: int) -> bool:
        """使用pywinauto关闭窗口"""
        if not PYWINAUTO_AVAILABLE:
            return False
        
        try:
            app = Application().connect(process=pid)
            app.kill()
            return True
        except Exception as e:
            self.logger.debug(f"pywinauto关闭失败: {e}")
            return False
    
    @handle_exception
    def wait_for_browser_close(self, timeout: float = 10.0) -> bool:
        """
        等待浏览器窗口关闭
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            bool: 是否在超时前关闭
        """
        def check_browser():
            has_browser = self.is_browser_open()
            return not has_browser, has_browser
        
        success, _ = wait_until(
            check_browser,
            timeout=timeout,
            interval=1.0,
            description="等待浏览器窗口关闭"
        )
        
        return success
    
    @handle_exception
    def close_all_browsers(self) -> int:
        """
        关闭所有浏览器（谨慎使用）
        
        Returns:
            int: 关闭的进程数量
        """
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil不可用，无法关闭所有浏览器")
            return 0
        
        closed_count = 0
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name:
                    for browser_names in self.browser_processes.values():
                        if any(
                            browser_name.lower() == proc_name.lower()
                            for browser_name in browser_names
                        ):
                            proc.terminate()
                            closed_count += 1
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            self.logger.info(f"已关闭 {closed_count} 个浏览器进程")
        
        return closed_count


# 测试函数
def test_browser_closer():
    """测试浏览器关闭器"""
    print("测试浏览器关闭器...")
    
    # 创建浏览器关闭器
    closer = BrowserCloser()
    
    # 测试是否有浏览器打开
    has_browser = closer.is_browser_open()
    print(f"是否有浏览器打开: {has_browser}")
    
    # 测试查找浏览器窗口
    windows = closer.find_browser_windows()
    print(f"找到 {len(windows)} 个浏览器窗口")
    
    for title, pid, browser_type in windows:
        print(f"  窗口: {title}, PID: {pid}, 浏览器: {browser_type}")
    
    # 测试关闭浏览器窗口（仅当有窗口时）
    if windows:
        closed_count = closer.close_browser_windows()
        print(f"关闭了 {closed_count} 个窗口")
    else:
        print("没有需要关闭的窗口")
    
    print("测试完成")


if __name__ == "__main__":
    test_browser_closer()