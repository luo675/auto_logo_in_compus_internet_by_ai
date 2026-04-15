# 校园网自动登录工具技术规格

## 1. 技术栈选择

### 1.1 核心编程语言
**Python 3.9+** (推荐理由)
- 跨平台支持，未来可扩展
- 丰富的自动化库生态系统
- 易于调试和维护
- 社区支持强大

### 1.2 关键依赖库

#### GUI自动化
- **pyautogui**: 屏幕坐标点击和键盘输入
- **pywinauto**: Windows GUI控件自动化 (更稳定)
- **keyboard**: 全局键盘监听 (可选)

#### 系统操作
- **subprocess**: 执行命令行工具
- **psutil**: 进程管理
- **schedule**: 定时任务 (备用)

#### 网络检测
- **requests**: HTTP请求测试
- **ping3**: ICMP ping测试
- **socket**: 底层网络检测

#### 配置和日志
- **configparser**: 配置文件解析
- **logging**: 标准日志模块
- **win10toast**: Windows通知

### 1.3 打包工具
- **PyInstaller**: 打包为exe
- **Inno Setup**: 创建安装程序 (可选)

## 2. 详细实现方案

### 2.1 模块分解

#### Module 1: 配置管理 (`config_manager.py`)
```python
class ConfigManager:
    def __init__(self):
        self.config_path = "config.ini"
        
    def load_config(self):
        # 读取账号、密码、路径配置
        pass
        
    def save_config(self):
        # 保存配置（加密存储密码）
        pass
        
    def get_credentials(self):
        # 从Windows Credential Manager获取
        pass
```

#### Module 2: 网页关闭模块 (`browser_closer.py`)
```python
class BrowserCloser:
    def __init__(self):
        self.browser_titles = [
            "校园网登录",
            "Dr.COM",
            "认证页面",
            "登录 -",
            "校园网"
        ]
        
    def find_browser_windows(self):
        # 查找包含校园网登录页面的浏览器窗口
        # 支持Chrome, Edge, Firefox, IE等
        pass
        
    def close_browser_windows(self):
        # 关闭检测到的校园网登录网页
        # 方法1: 发送Alt+F4或Ctrl+W
        # 方法2: 直接终止浏览器进程（谨慎使用）
        pass
        
    def is_browser_open(self):
        # 检查是否有校园网登录网页打开
        pass
```

#### Module 3: 网络状态检测 (`network_monitor.py`)
```python
class NetworkMonitor:
    def check_internet(self):
        # 方法1: Ping Google DNS
        # 方法2: HTTP请求测试
        # 方法3: 检测本地连接状态
        pass
        
    def check_vpn_residue(self):
        # 检测VPN残留的网络配置
        # 检查网络适配器状态
        pass
        
    def needs_repair(self):
        # 综合判断是否需要修复
        pass
```

#### Module 4: 修复工具调用 (`repair_executor.py`)
```python
class RepairExecutor:
    def __init__(self):
        self.huorong_path = r"D:\APP\huorongsecurity\Huorong\Sysdiag"
        
    def find_repair_tool(self):
        # 搜索火绒修复工具可执行文件
        # 可能文件名: hrfix.exe, hrnetfix.exe, netset.exe
        pass
        
    def run_repair(self, silent=True):
        # 执行修复命令
        # 尝试已知的命令行参数: /fix, /repair, /silent, /quiet
        pass
        
    def wait_for_completion(self, timeout=60):
        # 等待修复完成
        pass
```

#### Module 4: Dr.COM客户端自动化 (`drcom_automation.py`)
```python
class DrComAutomator:
    def __init__(self):
        self.client_path = r"C:\Users\luo\Desktop\APP\DrClient.exe"
        
    def start_client(self):
        # 启动Dr.COM客户端
        pass
        
    def is_client_running(self):
        # 检查客户端进程
        pass
        
    def is_logged_in(self):
        # 检测登录状态（通过窗口标题或网络状态）
        pass
        
    def perform_login(self, username, password):
        # 模拟登录操作
        # 1. 激活窗口
        # 2. 输入账号
        # 3. Tab到密码框
        # 4. 输入密码
        # 5. 点击登录按钮
        pass
        
    def logout(self):
        # 登出（如果需要）
        pass
```

#### Module 5: 日志和通知 (`logger_notifier.py`)
```python
class LoggerNotifier:
    def __init__(self):
        self.log_file = "auto_login.log"
        
    def log(self, level, message):
        # 记录日志到文件和控制台
        pass
        
    def notify_user(self, title, message, duration=5):
        # 发送Windows通知
        pass
        
    def send_error_alert(self, error):
        # 错误警报
        pass
```

#### Module 6: 主控制器 (`main_controller.py`)
```python
class MainController:
    def __init__(self):
        self.config = ConfigManager()
        self.browser = BrowserCloser()  # 新增：网页关闭模块
        self.network = NetworkMonitor()
        self.repair = RepairExecutor()
        self.drcom = DrComAutomator()
        self.logger = LoggerNotifier()
        
    def run(self):
        # 主流程控制
        pass
        
    def startup_sequence(self):
        # 开机启动序列
        pass
```

### 2.2 核心算法流程

```python
def main_workflow():
    # 1. 初始化
    logger.info("校园网自动登录工具启动")
    
    # 2. 等待网络初始化（开机后延迟）
    time.sleep(30)
    
    # 3. 检测网络状态
    if network.check_internet():
        logger.info("网络正常，尝试登录")
    else:
        logger.warning("网络异常，执行修复")
        if network.check_vpn_residue():
            logger.info("检测到VPN残留问题")
        
        # 执行修复
        repair.run_repair(silent=True)
        repair.wait_for_completion()
        
        # 重新检测
        if not network.check_internet():
            logger.error("修复失败，通知用户")
            notify_user("网络修复失败", "请手动检查网络")
            return False
    
    # 4. 启动Dr.COM客户端
    drcom.start_client()
    time.sleep(5)
    
    # 5. 检查登录状态
    if drcom.is_logged_in():
        logger.info("已登录，任务完成")
        return True
    
    # 6. 执行登录
    credentials = config.get_credentials()
    success = drcom.perform_login(
        credentials['username'],
        credentials['password']
    )
    
    # 7. 验证登录结果
    if success:
        logger.info("登录成功")
        notify_user("校园网登录", "自动登录成功")
        return True
    else:
        logger.error("登录失败")
        # 重试机制
        for i in range(3):
            logger.info(f"重试登录 ({i+1}/3)")
            if drcom.perform_login(...):
                return True
            time.sleep(10)
        
        notify_user("登录失败", "请手动登录校园网")
        return False
```

### 2.3 错误处理和恢复

#### 错误类型分类
1. **网络错误**: 重试3次，间隔10秒
2. **修复工具错误**: 尝试备用方案
3. **客户端错误**: 重启客户端进程
4. **登录错误**: 检查账号密码，重试

#### 恢复策略
```python
def error_recovery(error_type):
    strategies = {
        'network': [
            "重启网络适配器",
            "刷新DNS缓存",
            "重置Winsock"
        ],
        'client': [
            "重启Dr.COM客户端",
            "以管理员身份运行",
            "检查客户端版本"
        ],
        'repair': [
            "手动运行火绒修复",
            "使用Windows网络诊断",
            "重启系统"
        ]
    }
```

### 2.4 开机自启动实现

#### 方案A: Windows计划任务 (推荐)
```xml
<!-- 计划任务XML配置 -->
<triggers>
    <BootTrigger>
        <Delay>PT30S</Delay>
    </BootTrigger>
</triggers>
<actions>
    <Exec>
        <Command>C:\Program Files\AutoLoginTool\main.exe</Command>
    </Exec>
</actions>
```

#### 方案B: 注册表启动项
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
键名: CampusAutoLogin
值: "C:\Program Files\AutoLoginTool\main.exe"
```

#### 方案C: 启动文件夹
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

### 2.5 安全考虑

#### 密码存储方案
1. **Windows Credential Manager** (最安全)
   ```python
   import win32cred
   # 存储到Windows凭据管理器
   ```

2. **加密配置文件**
   ```python
   from cryptography.fernet import Fernet
   # 使用对称加密
   ```

3. **环境变量** (次选)
   ```python
   import os
   os.environ.get('CAMPUS_PASSWORD')
   ```

#### 权限管理
- 修复工具需要管理员权限
- 使用UAC提权或计划任务配置

### 2.6 测试计划

#### 单元测试
```python
# test_network_monitor.py
def test_check_internet():
    monitor = NetworkMonitor()
    assert monitor.check_internet() in [True, False]
```

#### 集成测试
1. 模拟网络正常场景
2. 模拟网络异常场景
3. 模拟修复过程
4. 模拟登录失败重试

#### 实际环境测试
- 在不同时间测试
- 测试VPN残留场景
- 测试长时间运行稳定性

### 2.7 部署方案

#### 步骤1: 开发环境搭建
```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2: 打包发布
```bash
# 使用PyInstaller打包
pyinstaller --onefile --windowed main.py

# 创建安装程序
# 使用Inno Setup或NSIS
```

#### 步骤3: 安装配置
1. 运行安装程序
2. 输入账号密码
3. 配置开机启动
4. 测试功能

#### 步骤4: 更新维护
- 定期检查日志
- 更新配置文件
- 处理客户端更新

## 3. 备选方案

### 方案B: AutoHotkey实现
- 优点: Windows原生，轻量级
- 缺点: 功能有限，维护困难

### 方案C: PowerShell实现
- 优点: 无需安装，系统自带
- 缺点: GUI自动化复杂

## 4. 风险评估和缓解

| 风险             | 概率 | 影响 | 缓解措施                     |
| ---------------- | ---- | ---- | ---------------------------- |
| 火绒工具路径变化 | 中   | 高   | 提供配置界面，支持自定义路径 |
| Dr.COM客户端更新 | 高   | 中   | 使用图像识别替代控件识别     |
| 网络环境变化     | 低   | 高   | 增加多种检测方法             |
| 权限不足         | 中   | 高   | 提供管理员权限说明           |
| 系统兼容性       | 低   | 中   | 支持Windows 10/11            |

## 5. 后续扩展功能

1. **多账号支持**: 切换不同账号
2. **网络测速**: 登录后测试网速
3. **流量监控**: 监控使用情况
4. **远程控制**: 通过Web界面控制
5. **移动端通知**: 推送登录状态到手机