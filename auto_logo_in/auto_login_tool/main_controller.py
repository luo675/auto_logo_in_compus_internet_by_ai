#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版主控制器模块
集成所有模块，实现完整的校园网自动登录流程
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# 导入自定义模块
from config import get_config_manager
from browser_closer import BrowserCloser
from network_checker import NetworkMonitor
from repair_tool import RepairExecutor
from login_automation import DrComAutomator
from utils.logging import get_logger_from_config


class MainController:
    """主控制器类（简化版）"""
    
    def __init__(self, config_path: str = "config.ini"):
        """
        初始化主控制器
        
        Args:
            config_path: 配置文件路径
        """
        # 初始化配置管理器
        self.config = get_config_manager(config_path)
        
        # 初始化日志记录器
        self.logger = get_logger_from_config(self.config)
        
        # 初始化各个模块
        self.browser = BrowserCloser(self.config)
        self.network = NetworkMonitor(self.config)
        self.repair = RepairExecutor(self.config)
        self.drcom = DrComAutomator(self.config)
        
        # 状态跟踪
        self.start_time = None
        self.operation_count = 0
        
        self.logger.info("主控制器初始化完成")
    
    def wait_for_system_ready(self):
        """等待系统启动完成"""
        startup_delay = self.config.get('settings', 'startup_delay', 30)
        self.logger.info(f"等待系统启动完成 ({startup_delay}秒)")
        
        for i in range(startup_delay):
            if i % 10 == 0:  # 每10秒记录一次
                self.logger.debug(f"等待系统启动... ({i}/{startup_delay}秒)")
            time.sleep(1)
        
        self.logger.info("系统启动等待完成")
    
    def close_browser_windows(self) -> Tuple[bool, str]:
        """关闭校园网登录网页"""
        self.logger.info("关闭浏览器窗口")
        
        try:
            # 检查是否有浏览器窗口打开
            has_browser = self.browser.is_browser_open()
            
            if not has_browser:
                self.logger.info("未找到校园网登录网页")
                return True, "未找到需要关闭的浏览器窗口"
            
            # 关闭浏览器窗口
            closed_count = self.browser.close_browser_windows()
            
            if closed_count > 0:
                # 等待浏览器关闭
                success = self.browser.wait_for_browser_close(10)
                
                if success:
                    msg = f"成功关闭 {closed_count} 个浏览器窗口"
                    self.logger.info(msg)
                    self.logger.send_success_notification("关闭浏览器窗口", msg)
                    return True, msg
                else:
                    msg = f"关闭了 {closed_count} 个窗口但等待超时"
                    self.logger.warning(msg)
                    self.logger.send_warning_notification("关闭浏览器窗口", msg)
                    return False, msg
            else:
                msg = "未成功关闭任何浏览器窗口"
                self.logger.warning(msg)
                self.logger.send_warning_notification("关闭浏览器窗口", msg)
                return False, msg
                
        except Exception as e:
            self.logger.error(f"关闭浏览器窗口时出错: {e}")
            self.logger.send_error_alert(e, "关闭浏览器窗口时出错")
            return False, f"关闭浏览器窗口时出错: {e}"
    
    def check_network_status(self) -> Tuple[str, str, Dict[str, Any]]:
        """检查网络状态"""
        self.logger.info("检查网络状态")
        
        try:
            # 检查网络状态
            needs_repair, reason, details = self.network.needs_repair()
            
            # 确定状态分类
            if not details['internet']['success']:
                status = 'offline'
            elif needs_repair:
                status = 'needs_repair'
            else:
                status = 'healthy'
            
            self.logger.info(f"网络状态: {status}, 原因: {reason}")
            return status, reason, details
            
        except Exception as e:
            self.logger.error(f"检查网络状态时出错: {e}")
            self.logger.send_error_alert(e, "检查网络状态时出错")
            return 'unknown', f"检查网络状态时出错: {e}", {}
    
    def perform_repair(self) -> Tuple[bool, str, Dict[str, Any]]:
        """执行网络修复"""
        self.logger.info("执行网络修复")
        
        try:
            # 运行完整修复流程
            success, message, details = self.repair.run_full_repair(
                silent=True,
                network_monitor=self.network
            )
            
            if success:
                self.logger.info(f"网络修复成功: {message}")
                self.logger.send_success_notification("网络修复", message)
            else:
                self.logger.warning(f"网络修复失败: {message}")
                self.logger.send_warning_notification("网络修复", message)
            
            return success, message, details
            
        except Exception as e:
            self.logger.error(f"执行网络修复时出错: {e}")
            self.logger.send_error_alert(e, "执行网络修复时出错")
            return False, f"执行网络修复时出错: {e}", {}
    
    def perform_login(self) -> Tuple[bool, str, Dict[str, Any]]:
        """执行登录操作"""
        self.logger.info("执行登录操作")
        
        try:
            # 获取凭据
            credentials = self.config.get_credentials()
            username = credentials.get('username', '')
            password = credentials.get('password', '')
            
            if not username or not password:
                msg = "未配置账号密码"
                self.logger.error(msg)
                self.logger.send_error_alert(msg, "登录失败")
                return False, msg, {}
            
            # 执行带重试的登录
            success, message, attempts = self.drcom.login_with_retry(username, password)
            
            details = {
                "username": username,
                "attempts": attempts,
                "success": success
            }
            
            if success:
                self.logger.info(f"登录成功: {message}")
                self.logger.send_success_notification("校园网登录", message)
            else:
                self.logger.warning(f"登录失败: {message}")
                self.logger.send_warning_notification("校园网登录", message)
            
            return success, message, details
            
        except Exception as e:
            self.logger.error(f"执行登录操作时出错: {e}")
            self.logger.send_error_alert(e, "执行登录操作时出错")
            return False, f"执行登录操作时出错: {e}", {}
    
    def handle_network_healthy(self) -> Tuple[bool, str, Dict[str, Any]]:
        """处理网络正常情况"""
        self.logger.info("网络正常，尝试登录")
        return self.perform_login()
    
    def handle_network_needs_repair(self) -> Tuple[bool, str, Dict[str, Any]]:
        """处理需要修复的网络情况"""
        self.logger.info("网络需要修复，执行修复流程")
        
        # 执行修复
        repair_success, repair_msg, repair_details = self.perform_repair()
        
        if not repair_success:
            return False, f"修复失败: {repair_msg}", {"repair": repair_details}
        
        # 修复后重新检查网络
        self.logger.info("修复完成，重新检查网络状态")
        time.sleep(10)  # 等待网络稳定
        
        status, reason, details = self.check_network_status()
        
        if status == 'healthy':
            # 网络恢复正常，尝试登录
            self.logger.info("修复后网络恢复正常，尝试登录")
            return self.perform_login()
        elif status == 'needs_repair':
            # 修复后仍然需要修复
            msg = f"修复后网络仍然需要修复: {reason}"
            self.logger.warning(msg)
            return False, msg, {"repair": repair_details, "recheck": details}
        else:  # offline or unknown
            msg = f"修复后网络状态: {status}, 原因: {reason}"
            self.logger.warning(msg)
            return False, msg, {"repair": repair_details, "recheck": details}
    
    def handle_network_offline(self) -> Tuple[bool, str, Dict[str, Any]]:
        """处理网络离线情况"""
        self.logger.warning("网络离线，尝试修复")
        
        # 尝试修复
        repair_success, repair_msg, repair_details = self.perform_repair()
        
        if not repair_success:
            return False, f"网络离线且修复失败: {repair_msg}", {"repair": repair_details}
        
        # 修复后重新检查网络
        self.logger.info("修复完成，重新检查网络")
        time.sleep(10)
        
        status, reason, details = self.check_network_status()
        
        if status == 'healthy':
            # 修复成功，网络恢复正常
            self.logger.info("修复后网络恢复正常，尝试登录")
            return self.perform_login()
        else:
            msg = f"修复后网络状态: {status}, 原因: {reason}"
            self.logger.warning(msg)
            return False, msg, {"repair": repair_details, "recheck": details}
    
    def run_workflow(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        运行完整工作流程
        
        Returns:
            Tuple[bool, str, Dict[str, Any]]: (是否成功, 状态信息, 详细信息)
        """
        self.start_time = time.time()
        
        self.logger.info("=" * 50)
        self.logger.info("开始校园网自动登录工作流程")
        self.logger.info("=" * 50)
        
        overall_success = False
        overall_message = ""
        overall_details = {
            "steps": [],
            "total_time": 0
        }
        
        try:
            # 步骤1: 等待系统启动完成
            self.wait_for_system_ready()
            overall_details["steps"].append({"name": "等待系统启动", "success": True})
            
            # 步骤2: 关闭校园网登录网页
            close_success, close_msg = self.close_browser_windows()
            overall_details["steps"].append({
                "name": "关闭浏览器窗口", 
                "success": close_success,
                "message": close_msg
            })
            
            # 步骤3: 检查网络状态
            status, reason, network_details = self.check_network_status()
            overall_details["steps"].append({
                "name": "检查网络状态",
                "success": True,
                "status": status,
                "reason": reason
            })
            
            overall_details["network_status"] = status
            overall_details["network_reason"] = reason
            overall_details["network_details"] = network_details
            
            # 步骤4: 根据网络状态执行相应操作
            if status == 'healthy':
                success, message, details = self.handle_network_healthy()
                operation = "直接登录"
            elif status == 'needs_repair':
                success, message, details = self.handle_network_needs_repair()
                operation = "修复后登录"
            elif status == 'offline':
                success, message, details = self.handle_network_offline()
                operation = "离线修复后登录"
            else:  # unknown
                success = False
                message = f"未知网络状态: {status}"
                details = {}
                operation = "未知状态处理"
            
            overall_details["steps"].append({
                "name": operation,
                "success": success,
                "message": message,
                "details": details
            })
            
            overall_success = success
            overall_message = message
            overall_details["operation"] = operation
            overall_details["operation_details"] = details
            
        except Exception as e:
            overall_success = False
            overall_message = f"工作流程执行异常: {e}"
            self.logger.send_error_alert(e, "工作流程执行异常")
            
            overall_details["steps"].append({
                "name": "异常处理",
                "success": False,
                "error": str(e)
            })
        
        # 计算总耗时
        total_time = time.time() - self.start_time
        overall_details["total_time"] = round(total_time, 2)
        
        # 记录最终结果
        self.logger.info("=" * 50)
        self.logger.info(f"工作流程完成，总耗时: {total_time:.2f}秒")
        self.logger.info(f"最终结果: {'成功' if overall_success else '失败'}")
        self.logger.info(f"最终消息: {overall_message}")
        self.logger.info("=" * 50)
        
        # 发送最终通知
        if overall_success:
            self.logger.send_success_notification(
                "校园网自动登录",
                f"登录成功，耗时: {total_time:.2f}秒"
            )
        else:
            self.logger.send_warning_notification(
                "校园网自动登录",
                f"登录失败: {overall_message}"
            )
        
        return overall_success, overall_message, overall_details
    
    def run_once(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        运行一次完整流程（兼容旧接口）
        
        Returns:
            Tuple[bool, str, Dict[str, Any]]: (是否成功, 状态信息, 详细信息)
        """
        return self.run_workflow()
    
    def startup_sequence(self):
        """
        开机启动序列
        这是计划任务调用的入口点
        """
        self.logger.info("开机启动序列开始")
        
        # 运行工作流程
        success, message, details = self.run_workflow()
        
        # 记录到专门的开机日志
        startup_log = Path("logs") / "startup.log"
        startup_log.parent.mkdir(exist_ok=True)
        
        with open(startup_log, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            status = "SUCCESS" if success else "FAILED"
            f.write(f"[{timestamp}] {status}: {message}\n")
        
        self.logger.info("开机启动序列结束")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="校园网自动登录工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 运行完整流程
  %(prog)s --config custom.ini # 使用自定义配置文件
  %(prog)s --debug            # 启用调试模式
  %(prog)s --test             # 运行测试模式
  %(prog)s --setup            # 初始设置向导
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.ini',
        help='配置文件路径 (默认: config.ini)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式（更详细的日志）'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='运行测试模式（不实际执行操作）'
    )
    
    parser.add_argument(
        '--setup', '-s',
        action='store_true',
        help='运行初始设置向导'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='校园网自动登录工具 v1.1.0 (简化版)'
    )
    
    return parser.parse_args()


def setup_wizard():
    """初始设置向导"""
    print("=" * 50)
    print("校园网自动登录工具 - 初始设置向导")
    print("=" * 50)
    
    # 检查依赖
    print("\n1. 检查依赖...")
    
    dependencies = [
        ('pywinauto', 'GUI自动化'),
        ('pyautogui', '键盘模拟'),
        ('psutil', '进程管理'),
        ('requests', '网络检测'),
        ('ping3', 'Ping检测'),
        ('win10toast', 'Windows通知'),
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}: 已安装 ({description})")
        except ImportError:
            print(f"  ✗ {module_name}: 未安装 ({description})")
    
    # 配置文件设置
    print("\n2. 配置文件设置...")
    config_path = input("配置文件路径 (默认: config.ini): ") or "config.ini"
    
    # 创建配置管理器
    config = get_config_manager(config_path)
    
    # 设置账号密码
    print("\n3. 设置校园网账号密码:")
    username = input("用户名: ")
    password = input("密码: ")
    
    config.save_credentials(username, password)
    
    # 验证路径
    print("\n4. 验证路径设置...")
    
    huorong_path = input(f"火绒安全软件路径 (默认: {config.get('paths', 'huorong_path')}): ")
    if huorong_path:
        config.set('paths', 'huorong_path', huorong_path)
    
    drcom_path = input(f"Dr.COM客户端路径 (默认: {config.get('paths', 'drcom_path')}): ")
    if drcom_path:
        config.set('paths', 'drcom_path', drcom_path)
    
    config.save_config()
    
    print("\n5. 设置完成!")
    print(f"配置文件: {config_path}")
    print("接下来可以运行: python main_controller.py 来测试工具")
    
    # 测试运行
    test_run = input("\n是否现在测试运行？(y/n): ").lower() == 'y'
    if test_run:
        main()


def test_mode():
    """测试模式"""
    print("=" * 50)
    print("校园网自动登录工具 - 测试模式")
    print("=" * 50)
    
    print("\n测试模式功能:")
    print("1. 检查配置")
    print("2. 测试网络检测")
    print("3. 测试浏览器关闭")
    print("4. 测试Dr.COM客户端检测")
    print("5. 测试修复工具查找")
    
    print("\n运行完整测试:")
    try:
        controller = MainController()
        print("主控制器初始化成功")
        
        # 测试网络检测
        status, reason, details = controller.check_network_status()
        print(f"网络状态: {status}, 原因: {reason}")
        
        # 测试浏览器检测
        has_browser = controller.browser.is_browser_open()
        print(f"浏览器是否打开: {has_browser}")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")


def main():
    """主函数"""
    args = parse_arguments()
    
    # 处理特殊参数
    if args.setup:
        setup_wizard()
        return
    
    if args.test:
        test_mode()
        return
    
    # 创建主控制器
    controller = MainController(args.config)
    
    # 设置日志级别
    if args.debug:
        # 临时提高日志级别
        import logging
        controller.logger.logger.setLevel(logging.DEBUG)
        for handler in controller.logger.logger.handlers:
            handler.setLevel(logging.DEBUG)
        controller.logger.info("调试模式已启用")
    
    # 运行工作流程
    success, message, details = controller.run_workflow()
    
    # 输出结果
    print("\n" + "=" * 50)
    print("校园网自动登录工具 - 运行结果")
    print("=" * 50)
    print(f"状态: {'成功' if success else '失败'}")
    print(f"消息: {message}")
    print(f"总耗时: {details.get('total_time', 0):.2f}秒")
    
    # 显示步骤详情
    print("\n步骤详情:")
    for i, step in enumerate(details.get('steps', []), 1):
        status = "✓" if step.get('success') else "✗"
        print(f"  {i}. {status} {step.get('name', '未知步骤')}")
        if 'message' in step:
            print(f"     消息: {step['message']}")
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()