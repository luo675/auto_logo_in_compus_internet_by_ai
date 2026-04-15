#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：获取所有窗口标题，帮助诊断Dr.COM窗口识别问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pywinauto
    from pywinauto import findwindows
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("pywinauto库未安装")
    sys.exit(1)

def get_all_windows():
    """获取所有可见窗口的标题"""
    print("正在获取所有可见窗口...")
    try:
        windows = findwindows.find_windows(visible_only=True)
        print(f"总共找到 {len(windows)} 个窗口")
        
        window_info = []
        for hwnd in windows:
            try:
                elem = findwindows.find_window(handle=hwnd)
                title = elem.window_text()
                if title:  # 只显示有标题的窗口
                    window_info.append((hwnd, title))
            except Exception as e:
                pass
        
        # 按标题排序
        window_info.sort(key=lambda x: x[1])
        
        print("\n=== 所有窗口标题 ===")
        for hwnd, title in window_info:
            print(f"{hwnd:10} : \"{title}\"")
        
        # 查找可能的Dr.COM窗口
        print("\n=== 可能的Dr.COM窗口 (包含关键词) ===")
        keywords = ['Dr', 'COM', '宽带', '认证', '客户端', '登录', 'Login', 'Client']
        drcom_windows = []
        for hwnd, title in window_info:
            if any(keyword.lower() in title.lower() for keyword in keywords):
                drcom_windows.append((hwnd, title))
                print(f"{hwnd:10} : \"{title}\"")
        
        if not drcom_windows:
            print("未找到包含关键词的窗口")
        
        return window_info
        
    except Exception as e:
        print(f"获取窗口时出错: {e}")
        return []

def test_window_connection():
    """测试连接到Dr.COM窗口"""
    print("\n=== 测试窗口连接 ===")
    
    # 尝试使用不同的进程名连接
    process_names = ['DrClient.exe', 'DrMain.exe', 'DrUpdate.exe']
    
    for proc_name in process_names:
        try:
            print(f"尝试连接进程: {proc_name}")
            from pywinauto import Application
            app = Application(backend='uia').connect(process=proc_name)
            windows = app.windows()
            print(f"  找到 {len(windows)} 个窗口")
            for i, w in enumerate(windows):
                print(f"    窗口 {i}: 标题=\"{w.window_text()}\", 类名=\"{w.class_name()}\"")
        except Exception as e:
            print(f"  连接失败: {e}")

if __name__ == "__main__":
    if not PYWINAUTO_AVAILABLE:
        print("请先安装pywinauto: pip install pywinauto")
        sys.exit(1)
    
    get_all_windows()
    test_window_connection()