# 校园网自动登录工具实现步骤

## 阶段1: 环境准备和调研 (1-2天)

### 步骤1.1: 确认技术细节
- [ ] 确认火绒修复工具的具体文件名和命令行参数
  - 方法: 手动检查 `D:\APP\huorongsecurity\Huorong\Sysdiag` 目录
  - 搜索可能的可执行文件: `*.exe`
  - 测试命令行参数: `工具名.exe /?` 或 `工具名.exe --help`

- [ ] 分析Dr.COM客户端界面
  - 截图记录登录窗口布局
  - 记录控件ID和窗口标题
  - 测试Tab键切换顺序

- [ ] 分析校园网登录网页
  - 记录浏览器窗口标题
  - 确定网页关闭方法
  - 测试不同浏览器（Chrome, Edge, Firefox）

- [ ] 确定网络检测方法
  - 测试ping命令可靠性
  - 测试HTTP请求目标 (校园网检测页面)
  - 确定VPN残留的检测方法

### 步骤1.2: 搭建开发环境
- [ ] 安装Python 3.9+
- [ ] 创建虚拟环境
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- [ ] 安装核心依赖
  ```bash
  pip install pyautogui pywinauto psutil requests ping3 win10toast
  ```

## 阶段2: 核心模块开发 (3-4天)

### 步骤2.1: 配置管理模块
- [ ] 创建 `config_manager.py`
  - 实现INI配置文件读写
  - 添加加密功能 (使用cryptography)
  - 集成Windows Credential Manager备选方案

- [ ] 创建配置文件模板 `config.ini.template`
  ```ini
  [credentials]
  username = 
  password = 
  
  [paths]
  huorong_path = D:\APP\huorongsecurity\Huorong\Sysdiag
  drcom_path = C:\Users\luo\Desktop\APP\DrClient.exe
  
  [settings]
  startup_delay = 30
  retry_count = 3
  retry_interval = 10
  ```

### 步骤2.2: 网络检测模块
- [ ] 创建 `network_monitor.py`
  - 实现ping检测函数
  - 实现HTTP连通性检测
  - 添加VPN残留检测逻辑
  - 创建网络状态综合评估方法

- [ ] 测试网络检测功能
  ```python
  # 测试脚本
  from network_monitor import NetworkMonitor
  monitor = NetworkMonitor()
  print(f"Internet: {monitor.check_internet()}")
  print(f"Needs repair: {monitor.needs_repair()}")
  ```

### 步骤2.3: 修复工具模块
- [ ] 创建 `repair_executor.py`
  - 实现火绒工具查找功能
  - 实现命令行参数测试
  - 添加修复进度监控
  - 实现超时和错误处理

- [ ] 测试修复功能
  ```python
  # 测试脚本 (谨慎运行)
  from repair_executor import RepairExecutor
  repair = RepairExecutor()
  tool_path = repair.find_repair_tool()
  print(f"Found tool: {tool_path}")
  # repair.run_repair(silent=True)  # 实际测试时启用
  ```

### 步骤2.4: 网页关闭模块
- [ ] 创建 `browser_closer.py`
  - 实现浏览器窗口检测功能
  - 实现校园网登录网页识别
  - 实现安全关闭网页的方法
  - 支持多种浏览器 (Chrome, Edge, Firefox, IE)

- [ ] 测试网页关闭功能
  ```python
  # 测试脚本
  from browser_closer import BrowserCloser
  closer = BrowserCloser()
  print(f"Browser open: {closer.is_browser_open()}")
  # closer.close_browser_windows()  # 实际测试时启用
  ```

### 步骤2.5: Dr.COM自动化模块
- [ ] 创建 `drcom_automation.py`
  - 实现客户端启动和进程管理
  - 实现窗口定位和激活
  - 实现账号密码自动输入
  - 实现登录状态检测

- [ ] 开发GUI识别策略
  - 方案A: 控件ID识别 (使用pywinauto)
  - 方案B: 图像匹配 (使用pyautogui)
  - 方案C: 坐标硬编码 (最后手段)

### 步骤2.6: 日志和通知模块
- [ ] 创建 `logger_notifier.py`
  - 配置logging模块
  - 实现文件和控制台双输出
  - 集成Windows toast通知
  - 添加错误级别分类

## 阶段3: 集成和主流程开发 (2-3天)

### 步骤3.1: 主控制器开发
- [ ] 创建 `main_controller.py`
  - 集成所有模块
  - 实现主工作流程
  - 添加错误处理和重试机制
  - 实现优雅退出

- [ ] 实现核心算法
  ```python
  def run(self):
      self.logger.info("启动校园网自动登录工具")
      
      # 1. 等待系统启动完成
      self._wait_for_system_ready()
      
      # 2. 检测网络状态
      network_status = self._check_network_status()
      
      # 3. 根据状态执行相应操作
      if network_status == 'healthy':
          return self._perform_login()
      elif network_status == 'needs_repair':
          return self._repair_and_login()
      else:
          return self._handle_error()
  ```

### 步骤3.2: 错误处理和恢复
- [ ] 实现错误分类和处理
  - 网络错误: 重试机制
  - 客户端错误: 重启策略
  - 修复错误: 备用方案
  - 登录错误: 账号密码验证

- [ ] 创建错误恢复策略
  ```python
  def recover_from_error(self, error_type):
      recovery_strategies = {
          'network': self._recover_network,
          'client': self._recover_client,
          'repair': self._recover_repair,
          'login': self._recover_login
      }
      return recovery_strategies.get(error_type, self._default_recovery)()
  ```

### 步骤3.3: 配置界面开发 (可选)
- [ ] 创建简单的GUI配置工具
  - 使用tkinter或PyQt
  - 账号密码输入
  - 路径配置
  - 测试按钮

## 阶段4: 测试和优化 (2-3天)

### 步骤4.1: 单元测试
- [ ] 为每个模块编写测试用例
  ```python
  # test_network_monitor.py
  def test_ping_success():
      # 模拟成功ping
      pass
      
  def test_ping_failure():
      # 模拟失败ping
      pass
  ```

- [ ] 创建测试环境
  - 模拟网络正常/异常状态
  - 模拟Dr.COM客户端
  - 模拟火绒修复工具

### 步骤4.2: 集成测试
- [ ] 测试完整流程
  1. 网络正常 → 直接登录
  2. 网络异常 → 修复 → 登录
  3. 登录失败 → 重试 → 成功
  4. 所有步骤失败 → 错误处理

- [ ] 压力测试
  - 连续运行24小时
  - 多次重启测试
  - 内存泄漏检查

### 步骤4.3: 实际环境测试
- [ ] 在真实环境中测试
  - 测试开机自启动
  - 测试VPN残留场景
  - 测试不同网络状况

- [ ] 收集反馈和优化
  - 调整等待时间
  - 优化错误提示
  - 改进用户体验

## 阶段5: 打包和部署 (1-2天)

### 步骤5.1: 打包为可执行文件
- [ ] 创建 `requirements.txt`
  ```txt
  pyautogui==0.9.53
  pywinauto==0.6.8
  psutil==5.9.5
  requests==2.28.2
  ping3==4.0.4
  win10toast==0.9
  cryptography==41.0.7
  ```

- [ ] 使用PyInstaller打包
  ```bash
  pyinstaller --onefile --windowed --name CampusAutoLogin main.py
  ```

- [ ] 测试打包后的exe文件
  - 在没有Python环境的机器上测试
  - 检查依赖是否完整
  - 验证功能正常

### 步骤5.2: 创建安装程序
- [ ] 编写安装脚本
  - 复制文件到Program Files
  - 创建开始菜单快捷方式
  - 配置开机启动

- [ ] 配置开机自启动
  ```python
  # 创建计划任务
  def create_scheduled_task():
      # 使用schtasks命令或python库
      pass
  ```

### 步骤5.3: 用户文档
- [ ] 编写README.md
  - 安装说明
  - 配置指南
  - 故障排除

- [ ] 创建使用教程
  - 截图说明配置步骤
  - 常见问题解答
  - 联系方式

## 阶段6: 维护和更新 (持续)

### 步骤6.1: 监控和日志分析
- [ ] 实现远程日志收集 (可选)
- [ ] 设置错误报警
- [ ] 定期检查工具状态

### 步骤6.2: 版本更新机制
- [ ] 实现自动更新检查
- [ ] 创建更新包
- [ ] 维护版本历史

### 步骤6.3: 用户支持
- [ ] 收集用户反馈
- [ ] 修复报告的问题
- [ ] 添加新功能

## 详细时间安排

```
第1周: 环境准备和核心模块开发
  Day 1-2: 技术调研和环境搭建
  Day 3-4: 配置管理和网络检测模块
  Day 5-6: 修复工具和Dr.COM自动化模块
  Day 7: 日志通知模块和初步集成

第2周: 集成测试和优化
  Day 8-9: 主控制器开发和错误处理
  Day 10-11: 单元测试和集成测试
  Day 12-13: 实际环境测试和优化
  Day 14: 打包和部署准备

第3周: 部署和维护
  Day 15: 打包发布
  Day 16: 用户测试和反馈
  后续: 维护和更新
```

## 关键成功因素

1. **准确的工具识别**: 确保能找到火绒修复工具和Dr.COM客户端
2. **稳定的GUI自动化**: 适应不同屏幕分辨率和窗口位置
3. **健壮的错误处理**: 应对各种异常情况
4. **用户友好的配置**: 简化安装和配置过程
5. **详细的日志记录**: 便于问题诊断

## 风险缓解措施

| 风险           | 应对策略                  |
| -------------- | ------------------------- |
| 火绒工具更新   | 提供配置界面自定义路径    |
| Dr.COM界面变化 | 使用图像识别增加容错      |
| 网络环境复杂   | 多种检测方法组合          |
| 权限问题       | 提供管理员运行说明        |
| 系统兼容性     | 支持Windows 10/11主流版本 |

## 验收标准

1. 工具能在开机后自动运行
2. 能正确检测网络状态
3. 网络异常时能自动修复
4. 能成功登录Dr.COM客户端
5. 提供详细的运行日志
6. 错误时能通知用户
7. 配置简单，易于使用

## 下一步行动

1. 开始阶段1的技术调研
2. 确认火绒工具的具体信息
3. 分析Dr.COM客户端界面结构
4. 搭建Python开发环境