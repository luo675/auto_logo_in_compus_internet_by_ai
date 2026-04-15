#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化配置管理工具
提供统一的配置加载和访问接口
"""

import os
import sys
import configparser
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class SimpleConfig:
    """
    简化配置管理器
    
    替代原有的复杂ConfigManager，提供基本功能：
    - 读取INI格式配置文件
    - 类型转换（int, float, bool, str）
    - 默认值支持
    - 简单的配置验证
    """
    
    def __init__(self, config_path: Union[str, Path] = "config.ini"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        
        # 默认配置
        self.defaults = {
            'credentials': {
                'username': '',
                'password': '',
            },
            'paths': {
                'huorong_path': r'D:\APP\huorongsecurity\Huorong\Sysdiag',
                'drcom_path': r'C:\Users\luo\Desktop\APP\DrClient.exe',
            },
            'settings': {
                'startup_delay': '30',
                'retry_count': '3',
                'retry_interval': '10',
                'network_timeout': '10',
                'repair_timeout': '60',
                'enable_notifications': 'true',
                'log_level': 'INFO',
            },
            'browser': {
                'browser_keywords': '校园网,登录,Dr.COM,认证',
                'close_method': 'alt_f4',
                'close_delay': '2',
            }
        }
        
        self.load_config()
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 是否成功加载
        """
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}，创建默认配置")
            self._create_default_config()
            return False
        
        try:
            self.config.read(self.config_path, encoding='utf-8')
            
            # 确保所有必需的节都存在
            for section, options in self.defaults.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for key, value in options.items():
                    if not self.config.has_option(section, key):
                        self.config.set(section, key, value)
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._create_default_config()
            return False
    
    def _create_default_config(self):
        """创建默认配置文件"""
        logger.info("创建默认配置文件")
        
        for section, options in self.defaults.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        
        self.save_config()
        logger.info(f"默认配置文件已创建: {self.config_path}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            logger.info(f"配置文件已保存: {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持自动类型转换
        
        Args:
            section: 节名
            key: 键名
            default: 默认值
        
        Returns:
            配置值（自动转换类型）
        """
        try:
            value = self.config.get(section, key)
            
            # 特殊处理布尔值
            if value.lower() in ('true', 'yes', '1', 'on'):
                return True
            elif value.lower() in ('false', 'no', '0', 'off'):
                return False
            
            # 尝试转换为整数
            try:
                return int(value)
            except ValueError:
                pass
            
            # 尝试转换为浮点数
            try:
                return float(value)
            except ValueError:
                pass
            
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """
        设置配置值
        
        Args:
            section: 节名
            key: 键名
            value: 值
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        # 转换值为字符串
        if isinstance(value, bool):
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value)
            
        self.config.set(section, key, value_str)
    
    def get_credentials(self) -> Dict[str, str]:
        """
        获取凭据（用户名和密码）
        
        Returns:
            Dict[str, str]: 包含username和password的字典
        """
        return {
            'username': self.get('credentials', 'username', ''),
            'password': self.get('credentials', 'password', ''),
        }
    
    def save_credentials(self, username: str, password: str):
        """
        保存凭据到配置文件
        
        Args:
            username: 用户名
            password: 密码
        """
        self.set('credentials', 'username', username)
        self.set('credentials', 'password', password)
        self.save_config()
        logger.info("凭据已保存到配置文件")
    
    def validate_paths(self) -> Dict[str, bool]:
        """
        验证配置的路径是否存在
        
        Returns:
            Dict[str, bool]: 路径验证结果
        """
        results = {}
        
        huorong_path = self.get('paths', 'huorong_path')
        if huorong_path:
            results['huorong_path'] = Path(huorong_path).exists()
            if not results['huorong_path']:
                logger.warning(f"火绒路径不存在: {huorong_path}")
        
        drcom_path = self.get('paths', 'drcom_path')
        if drcom_path:
            results['drcom_path'] = Path(drcom_path).exists()
            if not results['drcom_path']:
                logger.warning(f"Dr.COM客户端路径不存在: {drcom_path}")
        
        return results
    
    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        将配置转换为字典
        
        Returns:
            Dict[str, Dict[str, Any]]: 配置字典
        """
        result = {}
        for section in self.config.sections():
            result[section] = {}
            for key in self.config.options(section):
                result[section][key] = self.get(section, key)
        return result


# 全局配置管理器实例
_config_instance: Optional[SimpleConfig] = None


def get_config_manager(config_path: str = "config.ini") -> SimpleConfig:
    """
    获取配置管理器实例（单例模式）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        SimpleConfig: 配置管理器实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = SimpleConfig(config_path)
    
    return _config_instance


def reload_config(config_path: str = "config.ini") -> SimpleConfig:
    """
    重新加载配置管理器
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        SimpleConfig: 新的配置管理器实例
    """
    global _config_instance
    _config_instance = SimpleConfig(config_path)
    return _config_instance