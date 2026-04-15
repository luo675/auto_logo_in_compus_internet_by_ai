#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版火绒修复工具模块
查找并调用火绒断网修复工具
"""

import os
import sys
import time
import logging
import subprocess
import platform
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 导入工具模块
from .utils.wait import wait_until
from .utils.exceptions import RepairError, handle_exception


class RepairExecutor:
    """修复执行器类（简化版）"""
    
    def __init__(self, config_manager=None):
        """
        初始化修复执行器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 可能的火绒修复工具文件名
        self.possible_tool_names = [
            'hrfix.exe',           # 火绒修复工具
            'hrnetfix.exe',        # 火绒网络修复
            'netset.exe',          # 网络设置工具
            'repair.exe',          # 修复工具
            'hrfix64.exe',         # 64位修复工具
            'hrfix32.exe',         # 32位修复工具
        ]
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """从配置加载设置"""
        if self.config:
            self.huorong_path = Path(self.config.get('paths', 'huorong_path', 
                                                    r'D:\APP\huorongsecurity\Huorong\Sysdiag'))
            self.repair_timeout = self.config.get('settings', 'repair_timeout', 60)
        else:
            self.huorong_path = Path(r'D:\APP\huorongsecurity\Huorong\Sysdiag')
            self.repair_timeout = 60
        
        self.logger.debug(f"火绒路径: {self.huorong_path}")
        self.logger.debug(f"修复超时: {self.repair_timeout}秒")
    
    @handle_exception
    def find_repair_tool(self) -> Optional[Path]:
        """
        查找火绒修复工具可执行文件
        
        Returns:
            Optional[Path]: 找到的工具路径，未找到返回None
        """
        self.logger.info(f"在 {self.huorong_path} 中查找火绒修复工具")
        
        # 检查路径是否存在
        if not self.huorong_path.exists():
            self.logger.error(f"火绒路径不存在: {self.huorong_path}")
            return None
        
        # 首先尝试已知的工具名
        for tool_name in self.possible_tool_names:
            tool_path = self.huorong_path / tool_name
            if tool_path.exists():
                self.logger.info(f"找到修复工具: {tool_path}")
                return tool_path
        
        # 如果已知工具名都没找到，搜索目录下的所有exe文件
        self.logger.debug("已知工具名未找到，搜索所有exe文件")
        try:
            for item in self.huorong_path.iterdir():
                if item.is_file() and item.suffix.lower() == '.exe':
                    # 检查文件名是否包含修复相关关键词
                    name_lower = item.name.lower()
                    if any(keyword in name_lower for keyword in ['fix', 'repair', 'net', '网络']):
                        self.logger.info(f"找到可能的修复工具: {item}")
                        return item
        except Exception as e:
            self.logger.error(f"搜索修复工具时出错: {e}")
        
        self.logger.warning("未找到火绒修复工具")
        return None
    
    @handle_exception
    def run_repair_tool(self, tool_path: Path, silent: bool = True) -> Tuple[bool, str]:
        """
        运行修复工具
        
        Args:
            tool_path: 修复工具路径
            silent: 是否静默运行
        
        Returns:
            Tuple[bool, str]: (是否成功, 状态消息)
        """
        if not tool_path.exists():
            return False, f"修复工具不存在: {tool_path}"
        
        self.logger.info(f"运行修复工具: {tool_path}")
        
        try:
            # 构建命令行参数
            cmd = [str(tool_path)]
            
            if silent:
                # 尝试添加静默参数
                silent_args = ['/silent', '/quiet', '/s', '/q', '/auto']
                for arg in silent_args:
                    test_cmd = cmd + [arg]
                    try:
                        # 测试运行（快速超时）
                        result = subprocess.run(
                            test_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=2
                        )
                        if result.returncode == 0 or result.returncode == 1:
                            cmd = test_cmd
                            self.logger.debug(f"使用静默参数: {arg}")
                            break
                    except subprocess.TimeoutExpired:
                        # 超时表示程序可能已经启动
                        cmd = test_cmd
                        self.logger.debug(f"使用静默参数（超时）: {arg}")
                        break
                    except Exception:
                        continue
            
            # 运行修复工具
            self.logger.debug(f"执行命令: {' '.join(cmd)}")
            
            # 使用subprocess.Popen启动，不等待完成（修复工具可能需要时间）
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            # 等待一段时间让修复工具运行
            time.sleep(5)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                self.logger.info("修复工具正在运行，等待完成...")
                
                # 等待修复完成
                try:
                    process.wait(timeout=self.repair_timeout - 5)
                    return_code = process.returncode
                except subprocess.TimeoutExpired:
                    self.logger.warning("修复工具运行超时，强制终止")
                    process.terminate()
                    return False, "修复工具运行超时"
            else:
                return_code = process.returncode
            
            # 检查返回码
            if return_code == 0:
                return True, "修复工具运行成功"
            else:
                return False, f"修复工具返回错误码: {return_code}"
                
        except Exception as e:
            self.logger.error(f"运行修复工具时出错: {e}")
            return False, f"运行修复工具时出错: {e}"
    
    @handle_exception
    def run_system_repair_commands(self) -> List[Tuple[bool, str]]:
        """
        运行系统修复命令
        
        Returns:
            List[Tuple[bool, str]]: 命令执行结果列表
        """
        results = []
        
        if platform.system() != 'Windows':
            self.logger.warning("系统修复命令仅支持Windows")
            return results
        
        # Windows网络修复命令
        repair_commands = [
            ("重置Winsock", ['netsh', 'winsock', 'reset']),
            ("重置IP配置", ['netsh', 'int', 'ip', 'reset']),
            ("刷新DNS缓存", ['ipconfig', '/flushdns']),
            ("释放IP地址", ['ipconfig', '/release']),
            ("续订IP地址", ['ipconfig', '/renew']),
        ]
        
        for description, cmd in repair_commands:
            try:
                self.logger.info(f"执行系统修复命令: {description}")
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    text=True,
                    encoding='gbk'  # Windows中文编码
                )
                
                success = result.returncode == 0
                message = f"{description}: {'成功' if success else '失败'}"
                
                if not success and result.stderr:
                    message += f" - {result.stderr[:100]}"
                
                results.append((success, message))
                self.logger.debug(message)
                
            except Exception as e:
                error_msg = f"{description}执行出错: {e}"
                results.append((False, error_msg))
                self.logger.error(error_msg)
        
        return results
    
    @handle_exception
    def run_full_repair(
        self, 
        silent: bool = True,
        network_monitor = None
    ) -> Tuple[bool, str, Dict[str, any]]:
        """
        运行完整修复流程
        
        Args:
            silent: 是否静默运行
            network_monitor: 网络监控器实例（可选）
        
        Returns:
            Tuple[bool, str, Dict[str, any]]: (是否成功, 状态消息, 详细信息)
        """
        self.logger.info("开始完整修复流程")
        
        details = {
            'tool_found': False,
            'tool_success': False,
            'system_commands': [],
            'network_before': None,
            'network_after': None,
            'timestamp': time.time()
        }
        
        # 记录修复前的网络状态
        if network_monitor:
            try:
                details['network_before'] = network_monitor.check_internet()
            except Exception as e:
                self.logger.debug(f"记录修复前网络状态失败: {e}")
        
        # 1. 查找修复工具
        tool_path = self.find_repair_tool()
        details['tool_found'] = tool_path is not None
        
        if tool_path:
            # 2. 运行修复工具
            tool_success, tool_message = self.run_repair_tool(tool_path, silent)
            details['tool_success'] = tool_success
            details['tool_message'] = tool_message
            
            if tool_success:
                self.logger.info("修复工具运行成功")
            else:
                self.logger.warning(f"修复工具运行失败: {tool_message}")
        else:
            self.logger.warning("未找到修复工具，跳过工具修复")
        
        # 3. 运行系统修复命令
        system_results = self.run_system_repair_commands()
        details['system_commands'] = system_results
        
        system_success_count = sum(1 for success, _ in system_results if success)
        self.logger.info(f"系统修复命令执行完成: {system_success_count}/{len(system_results)} 成功")
        
        # 4. 等待网络稳定
        self.logger.info("等待网络稳定...")
        time.sleep(10)
        
        # 5. 检查修复后的网络状态
        if network_monitor:
            try:
                details['network_after'] = network_monitor.check_internet()
                
                # 判断修复是否成功
                if details['network_after']['success']:
                    success = True
                    message = "网络修复成功，互联网连接恢复"
                else:
                    success = False
                    message = "网络修复后互联网连接仍未恢复"
            except Exception as e:
                self.logger.error(f"检查修复后网络状态失败: {e}")
                success = False
                message = f"检查修复结果时出错: {e}"
        else:
            # 没有网络监控器，根据工具和命令执行情况判断
            tool_or_system_success = details.get('tool_success', False) or any(
                success for success, _ in system_results
            )
            
            if tool_or_system_success:
                success = True
                message = "修复流程执行完成"
            else:
                success = False
                message = "修复流程执行失败"
        
        self.logger.info(f"完整修复流程完成: {'成功' if success else '失败'}")
        return success, message, details


# 测试函数
def test_repair_executor():
    """测试修复执行器"""
    print("测试修复执行器...")
    
    # 创建修复执行器
    repair = RepairExecutor()
    
    # 测试查找修复工具
    tool_path = repair.find_repair_tool()
    print(f"找到修复工具: {tool_path}")
    
    # 测试运行系统修复命令
    system_results = repair.run_system_repair_commands()
    print(f"系统修复命令结果: {len(system_results)} 条")
    
    for success, message in system_results:
        print(f"  {'✓' if success else '✗'} {message}")
    
    print("测试完成")


if __name__ == "__main__":
    test_repair_executor()