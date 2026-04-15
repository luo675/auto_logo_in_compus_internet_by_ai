#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化配置管理模块
基于 utils.config.SimpleConfig 的兼容性包装
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 导入新的简化配置管理器
from .utils.config import SimpleConfig, get_config_manager as get_simple_config_manager

logger = logging.getLogger(__name__)


class ConfigManager(SimpleConfig):
    """
    配置管理器类（兼容性包装）
    
    为了保持向后兼容性，继承自 SimpleConfig 并添加旧版本的方法
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        logger.info("使用简化配置管理器")
    
    def save_credentials(
        self,
        username: str,
        password: str,
        use_windows: bool = True
    ) -> bool:
        """
        保存凭据（兼容旧接口）
        
        Args:
            username: 用户名
            password: 密码
            use_windows: 是否使用Windows凭据管理器（已弃用）
        
        Returns:
            bool: 是否成功
        """
        if use_windows:
            logger.warning("Windows凭据管理器功能已弃用，将保存到配置文件")
        
        try:
            self.set('credentials', 'username', username)
            self.set('credentials', 'password', password)
            self.save_config()
            logger.info("凭据已保存到配置文件")
            return True
        except Exception as e:
            logger.error(f"保存凭据失败: {e}")
            return False
    
    def load_credentials_from_windows(self) -> Optional[Dict[str, str]]:
        """
        从Windows凭据管理器加载凭据（已弃用）
        
        Returns:
            Dict[str, str]: 包含username和password的字典，失败返回None
        """
        logger.warning("Windows凭据管理器功能已弃用，返回空值")
        return None
    
    def save_credentials_to_windows(self, username: str, password: str) -> bool:
        """
        保存凭据到Windows凭据管理器（已弃用）
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            bool: 是否成功
        """
        logger.warning("Windows凭据管理器功能已弃用，不执行任何操作")
        return False
    
    def encrypt_password(self, password: str) -> str:
        """
        加密密码（已弃用）
        
        Args:
            password: 明文密码
        
        Returns:
            str: 原样返回密码（不加密）
        """
        logger.warning("密码加密功能已弃用，返回明文")
        return password
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """
        解密密码（已弃用）
        
        Args:
            encrypted_password: 加密的密码
        
        Returns:
            str: 原样返回密码
        """
        logger.warning("密码解密功能已弃用，返回原值")
        return encrypted_password


# 兼容性函数
def get_config_manager(config_path: str = "config.ini") -> ConfigManager:
    """
    获取配置管理器实例（兼容性函数）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        ConfigManager: 配置管理器实例
    """
    # 使用单例模式，但每次调用返回新实例以保持兼容性
    return ConfigManager(config_path)


# 测试函数
def test_config_manager():
    """测试配置管理器"""
    print("测试简化配置管理器...")
    
    config = ConfigManager("test_config.ini")
    
    # 测试获取值
    startup_delay = config.get('settings', 'startup_delay')
    print(f"启动延迟: {startup_delay} (类型: {type(startup_delay)})")
    
    # 测试设置值
    config.set('settings', 'test_key', 'test_value')
    
    # 测试凭据
    config.save_credentials('test_user', 'test_pass', use_windows=False)
    credentials = config.get_credentials()
    print(f"凭据: {credentials}")
    
    # 清理测试文件
    import os
    if os.path.exists("test_config.ini"):
        os.remove("test_config.ini")
    
    print("测试完成")


if __name__ == "__main__":
    test_config_manager()