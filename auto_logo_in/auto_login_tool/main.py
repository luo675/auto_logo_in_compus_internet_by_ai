#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园网自动登录工具 - 主入口文件
这是用户直接运行的文件，它会调用主控制器
"""

import os
import sys

# 添加当前目录到Python路径，确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入主控制器
from main_controller import main

if __name__ == "__main__":
    # 直接调用主控制器的主函数
    main()