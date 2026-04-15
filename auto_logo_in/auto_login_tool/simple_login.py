#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Dr.COM登录脚本 - 针对"网络选择"界面
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simple_login():
    """简化登录流程"""
    print("简化版Dr.COM登录")
    print("=" * 50)
    
    # 1. 启动Dr.COM客户端
    drcom_path = r'C:\Drcom\DrUpdateClient\DrMain.exe'
    if os.path.exists(drcom_path):
        print(f"1. 启动Dr.COM客户端: {drcom_path}")
        subprocess.Popen([drcom_path])
        time.sleep(5)
    else:
        print(f"错误: Dr.COM路径不存在: {drcom_path}")
        return False
    
    # 2. 使用pyautogui处理"网络选择"界面
    try:
        import pyautogui
        print("2. 使用pyautogui处理界面...")
        
        # 查找"网络选择"窗口
        time.sleep(2)
        windows = pyautogui.getWindowsWithTitle('网络选择')
        
        if windows:
            print(f"  找到'网络选择'窗口: {windows[0].title}")
            win = windows[0]
            
            # 激活窗口
            win.activate()
            time.sleep(1)
            
            # 方法1: 直接按回车（如果默认选择正确）
            print("  方法1: 尝试按回车键...")
            pyautogui.press('enter')
            time.sleep(3)
            
            # 检查是否进入登录界面
            login_windows = pyautogui.getWindowsWithTitle('Dr')
            if not login_windows:
                login_windows = pyautogui.getWindowsWithTitle('COM')
            if not login_windows:
                login_windows = pyautogui.getWindowsWithTitle('宽带')
            
            if login_windows:
                print(f"  进入登录界面: {login_windows[0].title}")
                
                # 激活登录窗口
                login_win = login_windows[0]
                login_win.activate()
                time.sleep(1)
                
                # 输入用户名
                print("  输入用户名: 506659")
                pyautogui.write('506659')
                time.sleep(0.5)
                
                # 切换到密码框
                pyautogui.press('tab')
                time.sleep(0.5)
                
                # 输入密码（需要实际密码）
                print("  输入密码: [需要实际密码]")
                # pyautogui.write('your_password_here')
                time.sleep(0.5)
                
                # 按回车登录
                print("  按回车登录")
                pyautogui.press('enter')
                
                print("  登录流程完成")
                return True
            else:
                print("  未检测到登录界面，可能已自动登录")
                return True
        else:
            print("  未找到'网络选择'窗口")
            
            # 尝试查找其他Dr.COM窗口
            all_windows = pyautogui.getAllWindows()
            dr_windows = []
            for w in all_windows:
                if w.title and ('Dr' in w.title or 'COM' in w.title or '宽带' in w.title or '认证' in w.title):
                    dr_windows.append(w)
            
            if dr_windows:
                print(f"  找到其他Dr.COM窗口: {[w.title for w in dr_windows]}")
                return True
            else:
                print("  未找到任何Dr.COM窗口")
                return False
                
    except ImportError:
        print("  pyautogui未安装，请运行: pip install pyautogui")
        return False
    except Exception as e:
        print(f"  操作失败: {e}")
        return False

def test_simple_workflow():
    """测试简化工作流程"""
    print("\n=== 测试简化工作流程 ===")
    
    # 检查网络状态
    print("1. 检查网络状态...")
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("  网络正常")
        network_ok = True
    except:
        print("  网络异常，可能需要修复")
        network_ok = False
    
    # 如果网络异常，运行火绒修复
    if not network_ok:
        print("2. 运行网络修复...")
        huorong_path = r'D:\APP\huorongsecurity\Huorong\Sysdiag\bin\NetDiag.exe'
        if os.path.exists(huorong_path):
            print(f"  运行火绒修复: {huorong_path}")
            subprocess.Popen([huorong_path])
            time.sleep(10)
        else:
            print(f"  火绒路径不存在: {huorong_path}")
    
    # 执行简化登录
    print("3. 执行简化登录...")
    success = simple_login()
    
    print("\n" + "=" * 50)
    if success:
        print("成功: 简化登录流程完成")
    else:
        print("失败: 简化登录失败")
    
    return success

if __name__ == "__main__":
    # 先杀死现有Dr.COM进程
    print("清理现有Dr.COM进程...")
    os.system('taskkill /f /im DrClient.exe 2>nul')
    os.system('taskkill /f /im DrMain.exe 2>nul')
    os.system('taskkill /f /im DrUpdate.exe 2>nul')
    time.sleep(2)
    
    # 测试简化工作流程
    test_simple_workflow()