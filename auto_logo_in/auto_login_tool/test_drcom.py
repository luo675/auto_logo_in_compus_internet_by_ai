#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Dr.COM客户端连接和窗口识别
"""

import sys
import os
import time
import subprocess

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_windows_api():
    """使用Windows API获取窗口标题"""
    print("=== 使用Windows API获取窗口标题 ===")
    
    try:
        import ctypes
        from ctypes import wintypes
        
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        
        titles = []
        
        def foreach_window(hwnd, lParam):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            if buff.value and len(buff.value.strip()) > 0:
                titles.append((hwnd, buff.value))
            return True
        
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        print(f"找到 {len(titles)} 个有标题的窗口")
        
        # 显示所有包含Dr/COM/宽带/认证的窗口
        print("\n=== 可能的Dr.COM窗口 ===")
        drcom_windows = []
        for hwnd, title in titles:
            if any(keyword in title for keyword in ['Dr', 'COM', '宽带', '认证', 'Client', 'Main', 'Update']):
                drcom_windows.append((hwnd, title))
                print(f"  {hwnd}: \"{title}\"")
        
        if not drcom_windows:
            print("未找到Dr.COM相关窗口")
            print("\n=== 前20个窗口标题 ===")
            for hwnd, title in titles[:20]:
                print(f"  {hwnd}: \"{title}\"")
        
        return drcom_windows
        
    except Exception as e:
        print(f"Windows API检测失败: {e}")
        return []

def test_pywinauto():
    """测试pywinauto连接"""
    print("\n=== 测试pywinauto连接 ===")
    
    try:
        import pywinauto
        from pywinauto import Application, findwindows
        
        # 检查进程
        print("检查Dr.COM进程...")
        os.system('tasklist | findstr /i dr')
        
        # 尝试连接
        print("\n尝试连接Dr.COM进程...")
        for proc_name in ['DrClient.exe', 'DrMain.exe', 'DrUpdate.exe']:
            try:
                print(f"  尝试连接 {proc_name}...")
                app = Application(backend='uia').connect(process=proc_name, timeout=3)
                windows = app.windows()
                print(f"    成功! 找到 {len(windows)} 个窗口")
                for w in windows:
                    print(f"      标题: \"{w.window_text()}\"")
                return True
            except Exception as e:
                print(f"    失败: {e}")
        
        return False
        
    except ImportError:
        print("pywinauto未安装")
        return False

def test_direct_login():
    """测试直接键盘模拟登录"""
    print("\n=== 测试直接键盘模拟登录 ===")
    
    # 启动Dr.COM客户端
    drcom_path = r'C:\Drcom\DrUpdateClient\DrMain.exe'
    if os.path.exists(drcom_path):
        print(f"启动Dr.COM客户端: {drcom_path}")
        subprocess.Popen([drcom_path])
        time.sleep(5)
        
        # 尝试使用pyautogui模拟键盘输入
        try:
            import pyautogui
            print("使用pyautogui模拟登录...")
            
            # 激活Dr.COM窗口（假设它在最前面）
            pyautogui.hotkey('alt', 'tab')
            time.sleep(1)
            
            # 输入用户名（需要根据实际界面调整）
            print("  模拟输入用户名...")
            pyautogui.write('506659')
            time.sleep(0.5)
            
            # 切换到密码框
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # 输入密码
            print("  模拟输入密码...")
            pyautogui.write('your_password')  # 需要替换为实际密码
            time.sleep(0.5)
            
            # 按回车登录
            print("  模拟按回车登录...")
            pyautogui.press('enter')
            
            print("登录模拟完成")
            return True
            
        except ImportError:
            print("pyautogui未安装")
            return False
    else:
        print(f"Dr.COM路径不存在: {drcom_path}")
        return False

def main():
    """主测试函数"""
    print("Dr.COM客户端连接测试")
    print("=" * 50)
    
    # 测试Windows API
    drcom_windows = test_windows_api()
    
    # 测试pywinauto
    pywinauto_success = test_pywinauto()
    
    if not drcom_windows and not pywinauto_success:
        print("\n=== 建议 ===")
        print("1. 确保Dr.COM客户端已启动")
        print("2. 检查窗口标题是否包含'Dr'、'COM'、'宽带'、'认证'等关键词")
        print("3. 如果窗口标题为空或不同，需要手动调整login_automation.py中的window_titles列表")
        
        # 提供手动测试
        print("\n=== 手动测试步骤 ===")
        print("1. 手动启动Dr.COM客户端")
        print("2. 查看窗口标题（通常在窗口顶部显示）")
        print("3. 将实际标题添加到login_automation.py的window_titles列表中")

if __name__ == "__main__":
    main()