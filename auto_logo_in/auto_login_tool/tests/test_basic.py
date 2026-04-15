#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本单元测试
测试重构后的核心功能
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import SimpleConfig
from utils.wait import wait_until
from utils.exceptions import CampusAutoLoginError


class TestSimpleConfig(unittest.TestCase):
    """测试简化配置管理器"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.ini"
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        config = SimpleConfig(str(self.config_path))
        
        # 检查默认值
        self.assertEqual(config.get('settings', 'startup_delay'), 30)
        self.assertEqual(config.get('settings', 'retry_count'), 3)
        self.assertTrue(config.get('settings', 'enable_notifications'))
        
        # 检查文件是否存在
        self.assertTrue(self.config_path.exists())
    
    def test_get_set_values(self):
        """测试获取和设置值"""
        config = SimpleConfig(str(self.config_path))
        
        # 设置值
        config.set('test_section', 'test_key', 'test_value')
        config.set('test_section', 'bool_key', True)
        config.set('test_section', 'int_key', 42)
        
        # 获取值
        self.assertEqual(config.get('test_section', 'test_key'), 'test_value')
        self.assertEqual(config.get('test_section', 'bool_key'), True)
        self.assertEqual(config.get('test_section', 'int_key'), 42)
        
        # 测试默认值
        self.assertEqual(config.get('test_section', 'nonexistent', 'default'), 'default')
    
    def test_get_credentials(self):
        """测试获取凭据"""
        config = SimpleConfig(str(self.config_path))
        
        # 设置凭据
        config.set('credentials', 'username', 'test_user')
        config.set('credentials', 'password', 'test_pass')
        
        credentials = config.get_credentials()
        self.assertEqual(credentials['username'], 'test_user')
        self.assertEqual(credentials['password'], 'test_pass')
    
    def test_save_credentials(self):
        """测试保存凭据"""
        config = SimpleConfig(str(self.config_path))
        
        config.save_credentials('user1', 'pass1')
        
        credentials = config.get_credentials()
        self.assertEqual(credentials['username'], 'user1')
        self.assertEqual(credentials['password'], 'pass1')


class TestWaitUtils(unittest.TestCase):
    """测试等待工具"""
    
    def test_wait_until_success(self):
        """测试等待成功条件"""
        # 创建一个立即成功的条件
        def success_condition():
            return True, "success data"
        
        success, data = wait_until(
            success_condition,
            timeout=1.0,
            interval=0.1,
            description="测试成功条件"
        )
        
        self.assertTrue(success)
        self.assertEqual(data, "success data")
    
    def test_wait_until_timeout(self):
        """测试等待超时"""
        # 创建一个永远失败的条件
        def failure_condition():
            return False, "failure data"
        
        success, data = wait_until(
            failure_condition,
            timeout=0.5,
            interval=0.1,
            description="测试超时条件"
        )
        
        self.assertFalse(success)
        self.assertEqual(data, "failure data")
    
    @patch('time.sleep')
    def test_wait_until_with_retry(self, mock_sleep):
        """测试带重试的等待"""
        call_count = 0
        
        def condition():
            nonlocal call_count
            call_count += 1
            return call_count >= 3, f"call {call_count}"
        
        success, data = wait_until(
            condition,
            timeout=5.0,
            interval=0.1,
            description="测试重试条件"
        )
        
        self.assertTrue(success)
        self.assertEqual(data, "call 3")
        self.assertGreaterEqual(mock_sleep.call_count, 2)


class TestExceptions(unittest.TestCase):
    """测试异常类"""
    
    def test_custom_exceptions(self):
        """测试自定义异常"""
        # 测试基础异常
        with self.assertRaises(CampusAutoLoginError):
            raise CampusAutoLoginError("测试错误")
        
        # 测试派生异常
        from utils.exceptions import NetworkError, AuthenticationError
        
        with self.assertRaises(NetworkError):
            raise NetworkError("网络错误")
        
        with self.assertRaises(AuthenticationError):
            raise AuthenticationError("认证错误")
    
    def test_handle_exception_decorator(self):
        """测试异常处理装饰器"""
        from utils.exceptions import handle_exception
        
        @handle_exception
        def good_function():
            return "success"
        
        @handle_exception
        def bad_function():
            raise ValueError("测试错误")
        
        # 测试正常函数
        result = good_function()
        self.assertEqual(result, "success")
        
        # 测试异常函数
        with self.assertRaises(CampusAutoLoginError):
            bad_function()


# 模拟测试（不实际运行GUI操作）
class TestModuleImports(unittest.TestCase):
    """测试模块导入"""
    
    def test_import_config_module(self):
        """测试配置模块导入"""
        from config import ConfigManager, get_config_manager
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[test]\nkey=value\n")
            temp_path = f.name
        
        try:
            config = ConfigManager(temp_path)
            self.assertIsNotNone(config)
            
            config2 = get_config_manager(temp_path)
            self.assertIsNotNone(config2)
        finally:
            os.unlink(temp_path)
    
    @patch('pywinauto.Application')
    @patch('psutil.process_iter')
    def test_mock_imports(self, mock_process_iter, mock_application):
        """测试模拟导入"""
        # 模拟psutil.process_iter返回空列表
        mock_process_iter.return_value = []
        
        # 模拟pywinauto.Application
        mock_app = MagicMock()
        mock_application.return_value = mock_app
        
        # 这些导入应该成功（即使没有实际安装依赖）
        # 我们只是测试导入是否不会引发异常
        try:
            from browser_closer import BrowserCloser
            from network_checker import NetworkMonitor
            from repair_tool import RepairExecutor
            from login_automation import DrComAutomator
            
            # 创建模拟配置
            mock_config = Mock()
            mock_config.get.return_value = "test_value"
            
            # 测试创建实例（使用模拟）
            with patch.dict('sys.modules', {'pywinauto': MagicMock(), 'psutil': MagicMock()}):
                closer = BrowserCloser(mock_config)
                monitor = NetworkMonitor(mock_config)
                repair = RepairExecutor(mock_config)
                automator = DrComAutomator(mock_config)
                
                self.assertIsNotNone(closer)
                self.assertIsNotNone(monitor)
                self.assertIsNotNone(repair)
                self.assertIsNotNone(automator)
                
        except ImportError as e:
            # 某些依赖可能未安装，这是可以接受的
            print(f"导入警告: {e}")
            self.skipTest(f"跳过测试，依赖未安装: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)