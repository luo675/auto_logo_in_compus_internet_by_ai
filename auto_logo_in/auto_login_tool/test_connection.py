#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试Dr.COM客户端连接问题
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pywinauto_direct():
    """直接测试pywinauto连接"""
    print("=== 直接测试pywinauto连接 ===")
    
    try:
        import pywinauto
        from pywinauto import Application
        
        # 检查进程
        print("当前Dr.COM进程:")
        os.system('tasklist | findstr /i dr')
        
        # 尝试不同的连接方法
        test_cases = [
            # (方法描述, 连接参数)
            ("通过进程名DrClient.exe", {'process': 'DrClient.exe'}),
            ("通过进程名DrMain.exe", {'process': 'DrMain.exe'}),
            ("通过进程名DrUpdate.exe", {'process': 'DrUpdate.exe'}),
            ("通过标题正则", {'title_re': '.*Dr.*COM.*'}),
            ("通过标题包含Dr", {'title': 'Dr.COM 宽带认证客户端'}),
            ("通过标题包含宽带", {'title': '宽带认证客户端'}),
        ]
        
        for desc, kwargs in test_cases:
            print(f"\n尝试: {desc}")
            try:
                # 尝试uia backend
                app = Application(backend='uia').connect(**kwargs, timeout=3)
                windows = app.windows()
                print(f"  uia backend成功! 找到 {len(windows)} 个窗口")
                for w in windows:
                    print(f"    标题: \"{w.window_text()}\"")
                return app
            except Exception as e:
                print(f"  uia backend失败: {e}")
                
            try:
                # 尝试win32 backend
                app = Application(backend='win32').connect(**kwargs, timeout=3)
                windows = app.windows()
                print(f"  win32 backend成功! 找到 {len(windows)} 个窗口")
                for w in windows:
                    print(f"    标题: \"{w.window_text()}\"")
                return app
            except Exception as e:
                print(f"  win32 backend失败: {e}")
        
        return None
        
    except ImportError as e:
        print(f"pywinauto导入失败: {e}")
        return None

def test_windows_direct():
    """使用Windows API直接获取窗口信息"""
    print("\n=== 使用Windows API获取窗口信息 ===")
    
    try:
        import ctypes
        from ctypes import wintypes
        
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        
        windows = []
        
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    if buff.value:
                        windows.append((hwnd, buff.value))
            return True
        
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        print(f"找到 {len(windows)} 个可见窗口")
        
        # 显示Dr.COM相关窗口
        print("\nDr.COM相关窗口:")
        dr_windows = []
        for hwnd, title in windows:
            if any(keyword in title for keyword in ['Dr', 'COM', '宽带', '认证']):
                dr_windows.append((hwnd, title))
                print(f"  {hwnd}: \"{title}\"")
        
        if not dr_windows:
            print("未找到Dr.COM窗口，显示前20个窗口:")
            for hwnd, title in windows[:20]:
                print(f"  {hwnd}: \"{title}\"")
        
        return dr_windows
        
    except Exception as e:
        print(f"Windows API失败: {e}")
        return []

def test_manual_workaround():
    """测试手动解决方法"""
    print("\n=== 测试手动解决方法 ===")
    
    # 1. 确保Dr.COM已启动
    drcom_path = r'C:\Drcom\DrUpdateClient\DrMain.exe'
    if os.path.exists(drcom_path):
        print("1. 启动Dr.COM客户端...")
        subprocess.Popen([drcom_path])
        time.sleep(5)
    
    # 2. 使用pyautogui直接操作
    try:
        import pyautogui
        print("2. 使用pyautogui定位窗口...")
        
        # 查找Dr.COM窗口
        windows = pyautogui.getWindowsWithTitle('Dr')
        if not windows:
            windows = pyautogui.getWindowsWithTitle('COM')
        if not windows:
            windows = pyautogui.getWindowsWithTitle('宽带')
        
        if windows:
            print(f"  找到 {len(windows)} 个相关窗口")
            for i, win in enumerate(windows):
                print(f"    窗口{i}: 标题=\"{win.title}\", 位置={win.left},{win.top}")
            
            # 激活第一个窗口
            win = windows[0]
            win.activate()
            time.sleep(1)
            
            print("3. 模拟登录操作...")
            # 输入用户名
            pyautogui.write('506659')
            time.sleep(0.5)
            pyautogui.press('tab')
            time.sleep(0.5)
            # 输入密码（需要实际密码）
            # pyautogui.write('your_password')
            # time.sleep(0.5)
            # pyautogui.press('enter')
            
            print("  模拟操作完成（密码部分已注释）")
            return True
        else:
            print("  未找到相关窗口")
            return False
            
    except ImportError:
        print("  pyautogui未安装")
        return False

def main():
    """主测试函数"""
    print("Dr.COM客户端连接详细测试")
    print("=" * 60)
    
    # 测试1: 直接pywinauto连接
    app = test_pywinauto_direct()
    
    # 测试2: Windows API
    dr_windows = test_windows_direct()
    
    # 测试3: 手动解决方法
    if not app and not dr_windows:
        print("\n所有自动方法失败，尝试手动解决方法...")
        test_manual_workaround()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    if app:
        print("✓ 成功通过pywinauto连接到Dr.COM客户端")
    elif dr_windows:
        print("✓ 检测到Dr.COM窗口，但pywinauto连接失败")
        print("  实际窗口标题:", dr_windows[0][1] if dr_windows else "无")
    else:
        print("✗ 所有连接方法失败")
        print("\n建议:")
        print("1. 确保Dr.COM客户端已手动启动")
        print("2. 检查窗口标题（可能包含特殊字符或编码问题）")
        print("3. 尝试以管理员身份运行此测试")
        print("4. 考虑使用备用登录方法（键盘模拟）")

if __name__ == "__main__":
    main()