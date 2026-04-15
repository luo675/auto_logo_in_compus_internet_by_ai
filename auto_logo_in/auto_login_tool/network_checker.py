#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版网络检测模块
检测网络连通性、VPN残留问题，判断是否需要修复
"""

import os
import sys
import time
import socket
import logging
import subprocess
import platform
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 导入工具模块
from .utils.wait import wait_until
from .utils.exceptions import NetworkError, ConnectionError, handle_exception

# 尝试导入网络检测库
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests库未安装，HTTP检测功能受限")

try:
    import ping3
    PING3_AVAILABLE = True
except ImportError:
    PING3_AVAILABLE = False
    logging.warning("ping3库未安装，Ping检测功能受限")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil库未安装，网络适配器检测功能受限")


class NetworkMonitor:
    """网络监控器类（简化版）"""
    
    def __init__(self, config_manager=None):
        """
        初始化网络监控器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 网络检测目标
        self.ping_targets = [
            '8.8.8.8',           # Google DNS
            '1.1.1.1',           # Cloudflare DNS
            '114.114.114.114',   # 国内DNS
            '223.5.5.5',         # 阿里DNS
        ]
        
        self.http_targets = [
            'http://connectivitycheck.gstatic.com/generate_204',
            'http://www.baidu.com',
            'http://www.qq.com',
        ]
        
        # VPN相关进程和适配器
        self.vpn_processes = [
            'clash.exe', 'v2ray.exe', 'shadowsocks.exe', 'openvpn.exe',
            'wireguard.exe', 'zerotier.exe', 'tailscale.exe',
        ]
        
        self.vpn_adapters = [
            'tap', 'tun', 'wireguard', 'zerotier', 'tailscale',
            'openvpn', 'softether', 'pptp', 'l2tp', 'ipsec'
        ]
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """从配置加载设置"""
        if self.config:
            self.network_timeout = self.config.get('settings', 'network_timeout', 10)
        else:
            self.network_timeout = 10
        
        self.logger.debug(f"网络检测超时: {self.network_timeout}秒")
    
    @handle_exception
    def check_internet(self, method: str = 'auto') -> Dict[str, any]:
        """
        检测互联网连通性
        
        Args:
            method: 检测方法 ('ping', 'http', 'auto')
        
        Returns:
            Dict[str, any]: 检测结果
        """
        self.logger.debug(f"检查互联网连通性，方法: {method}")
        
        if method == 'auto':
            # 尝试ping，如果失败则尝试http
            ping_result = self._check_ping()
            if ping_result['success']:
                return ping_result
            return self._check_http()
        elif method == 'ping':
            return self._check_ping()
        elif method == 'http':
            return self._check_http()
        else:
            raise ValueError(f"未知的检测方法: {method}")
    
    def _check_ping(self) -> Dict[str, any]:
        """使用ping检测网络连通性"""
        results = []
        
        for target in self.ping_targets[:2]:  # 只测试前两个目标
            success = False
            latency = None
            
            if PING3_AVAILABLE:
                try:
                    latency = ping3.ping(target, timeout=2)
                    success = latency is not None and latency > 0
                except Exception as e:
                    self.logger.debug(f"ping3检测失败 {target}: {e}")
                    success = False
            else:
                # 使用系统ping命令
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '2', '-w', '2000', target]
                
                try:
                    result = subprocess.run(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=3
                    )
                    success = result.returncode == 0
                except Exception as e:
                    self.logger.debug(f"系统ping检测失败 {target}: {e}")
                    success = False
            
            results.append({
                'target': target,
                'success': success,
                'latency': latency
            })
            
            if success:
                break  # 只要有一个成功就认为网络正常
        
        overall_success = any(r['success'] for r in results)
        
        return {
            'method': 'ping',
            'success': overall_success,
            'results': results,
            'timestamp': time.time()
        }
    
    def _check_http(self) -> Dict[str, any]:
        """使用HTTP请求检测网络连通性"""
        if not REQUESTS_AVAILABLE:
            return {
                'method': 'http',
                'success': False,
                'error': 'requests库未安装',
                'timestamp': time.time()
            }
        
        results = []
        
        for url in self.http_targets[:2]:  # 只测试前两个目标
            success = False
            status_code = None
            response_time = None
            
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time
                status_code = response.status_code
                
                # 204状态码或2xx状态码都算成功
                success = response.ok or status_code == 204
                
            except Exception as e:
                self.logger.debug(f"HTTP检测失败 {url}: {e}")
                success = False
            
            results.append({
                'url': url,
                'success': success,
                'status_code': status_code,
                'response_time': response_time
            })
            
            if success:
                break  # 只要有一个成功就认为网络正常
        
        overall_success = any(r['success'] for r in results)
        
        return {
            'method': 'http',
            'success': overall_success,
            'results': results,
            'timestamp': time.time()
        }
    
    @handle_exception
    def check_vpn(self) -> Dict[str, any]:
        """
        检查VPN残留问题
        
        Returns:
            Dict[str, any]: VPN检测结果
        """
        self.logger.debug("检查VPN残留问题")
        
        process_results = []
        adapter_results = []
        
        # 检查VPN进程
        if PSUTIL_AVAILABLE:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name:
                        proc_name_lower = proc_name.lower()
                        for vpn_proc in self.vpn_processes:
                            if vpn_proc in proc_name_lower:
                                process_results.append({
                                    'name': proc_name,
                                    'pid': proc.pid,
                                    'vpn_type': vpn_proc
                                })
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # 检查网络适配器（Windows）
        if platform.system().lower() == 'windows':
            try:
                import wmi
                c = wmi.WMI()
                for adapter in c.Win32_NetworkAdapter():
                    if adapter.NetEnabled and adapter.Name:
                        adapter_name = adapter.Name.lower()
                        for vpn_adapter in self.vpn_adapters:
                            if vpn_adapter in adapter_name:
                                adapter_results.append({
                                    'name': adapter.Name,
                                    'adapter_type': vpn_adapter
                                })
                                break
            except ImportError:
                self.logger.debug("wmi库未安装，无法检测VPN适配器")
            except Exception as e:
                self.logger.debug(f"检测VPN适配器失败: {e}")
        
        has_vpn_process = len(process_results) > 0
        has_vpn_adapter = len(adapter_results) > 0
        has_vpn = has_vpn_process or has_vpn_adapter
        
        return {
            'has_vpn': has_vpn,
            'has_vpn_process': has_vpn_process,
            'has_vpn_adapter': has_vpn_adapter,
            'processes': process_results,
            'adapters': adapter_results,
            'timestamp': time.time()
        }
    
    @handle_exception
    def check_dns(self) -> Dict[str, any]:
        """
        检查DNS解析
        
        Returns:
            Dict[str, any]: DNS检测结果
        """
        self.logger.debug("检查DNS解析")
        
        test_domains = ['www.baidu.com', 'www.google.com', 'www.qq.com']
        results = []
        
        for domain in test_domains:
            success = False
            ip_address = None
            
            try:
                ip_address = socket.gethostbyname(domain)
                success = ip_address is not None
            except Exception as e:
                self.logger.debug(f"DNS解析失败 {domain}: {e}")
                success = False
            
            results.append({
                'domain': domain,
                'success': success,
                'ip_address': ip_address
            })
        
        overall_success = any(r['success'] for r in results)
        
        return {
            'success': overall_success,
            'results': results,
            'timestamp': time.time()
        }
    
    @handle_exception
    def needs_repair(self) -> Tuple[bool, str, Dict[str, any]]:
        """
        判断是否需要网络修复
        
        Returns:
            Tuple[bool, str, Dict[str, any]]: 
                (是否需要修复, 原因, 详细检测结果)
        """
        self.logger.info("判断是否需要网络修复")
        
        details = {
            'internet': None,
            'vpn': None,
            'dns': None,
            'timestamp': time.time()
        }
        
        # 检查互联网连通性
        internet_result = self.check_internet()
        details['internet'] = internet_result
        
        if not internet_result['success']:
            return True, "互联网连接失败", details
        
        # 检查VPN残留
        vpn_result = self.check_vpn()
        details['vpn'] = vpn_result
        
        if vpn_result['has_vpn']:
            return True, "检测到VPN残留", details
        
        # 检查DNS解析
        dns_result = self.check_dns()
        details['dns'] = dns_result
        
        if not dns_result['success']:
            return True, "DNS解析失败", details
        
        # 所有检查通过，不需要修复
        return False, "网络状态正常", details
    
    @handle_exception
    def wait_for_network(self, timeout: float = 60.0) -> bool:
        """
        等待网络恢复正常
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            bool: 是否在超时前网络恢复正常
        """
        self.logger.info(f"等待网络恢复正常，超时: {timeout}秒")
        
        def check_network():
            internet_result = self.check_internet()
            return internet_result['success'], internet_result
        
        success, result = wait_until(
            check_network,
            timeout=timeout,
            interval=5.0,
            description="等待网络恢复正常"
        )
        
        if success:
            self.logger.info("网络已恢复正常")
        else:
            self.logger.warning(f"等待网络恢复超时（{timeout}秒）")
        
        return success


# 测试函数
def test_network_monitor():
    """测试网络监控器"""
    print("测试网络监控器...")
    
    # 创建网络监控器
    monitor = NetworkMonitor()
    
    # 测试互联网连通性
    internet_result = monitor.check_internet()
    print(f"互联网连通性: {internet_result['success']}")
    
    # 测试VPN检测
    vpn_result = monitor.check_vpn()
    print(f"VPN检测: {vpn_result['has_vpn']}")
    
    # 测试DNS检测
    dns_result = monitor.check_dns()
    print(f"DNS解析: {dns_result['success']}")
    
    # 测试是否需要修复
    needs_repair, reason, details = monitor.needs_repair()
    print(f"是否需要修复: {needs_repair}, 原因: {reason}")
    
    print("测试完成")


if __name__ == "__main__":
    test_network_monitor()