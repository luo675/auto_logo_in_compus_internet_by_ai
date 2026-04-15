# 校园网自动登录工具 - 用户详细操作指南

## 概述

本指南将详细指导您如何配置、测试和使用校园网自动登录工具。请按照步骤顺序操作。

## 第一步：环境准备

### 1.1 检查Python环境
1. 打开命令提示符（Win+R，输入`cmd`，回车）
2. 输入以下命令检查Python是否安装：
   ```
   python --version
   ```
3. 如果显示Python 3.9或更高版本，继续下一步
4. 如果未安装Python，请访问 https://www.python.org/downloads/ 下载并安装

### 1.2 下载工具文件
1. 确保您有完整的工具文件，目录结构如下：
   ```
   auto_login_tool/
   ├── main.py
   ├── main_controller.py
   ├── config.py
   ├── browser_closer.py
   ├── network_checker.py
   ├── repair_tool.py
   ├── login_automation.py
   ├── logger.py
   ├── requirements.txt
   ├── config.ini.template
   ├── install.bat
   ├── README.md
   └── logs/ (目录)
   ```

## 第二步：安装和配置

### 2.1 运行安装脚本（推荐）
1. 进入工具目录：
   ```
   cd auto_login_tool
   ```
2. 运行安装脚本：
   ```
   install.bat
   ```
3. 按照脚本提示完成安装

### 2.2 手动安装（如果脚本失败）
1. 安装Python依赖：
   ```
   pip install -r requirements.txt
   ```
2. 如果遇到权限问题，尝试：
   ```
   pip install --user -r requirements.txt
   ```

### 2.3 运行设置向导
1. 在工具目录中运行：
   ```
   python main.py --setup
   ```
2. 按照向导提示输入信息：

   **必须配置的信息：**
   - **校园网账号**：您的校园网登录账号
   - **密码**：您的校园网密码
   - **存储方式**：建议使用Windows凭据管理器（更安全）

   **路径配置（重要！）：**
   - **火绒安全软件路径**：
     - 默认：`D:\APP\huorongsecurity\Huorong\Sysdiag`
     - 确认方法：打开文件资源管理器，导航到火绒安装目录
     - 如果路径不同，请修改为实际路径

   - **Dr.COM客户端路径**：
     - 默认：`C:\Users\luo\Desktop\APP\DrClient.exe`
     - 确认方法：找到Dr.COM客户端的实际位置
     - 如果路径不同，请修改为实际路径

3. 设置完成后，会在目录中生成`config.ini`文件

### 2.4 验证配置文件
1. 打开`config.ini`文件检查配置是否正确
2. 重点检查以下部分：
   ```ini
   [paths]
   huorong_path = D:\APP\huorongsecurity\Huorong\Sysdiag  ; 确认此路径存在
   drcom_path = C:\Users\luo\Desktop\APP\DrClient.exe     ; 确认此路径存在
   ```

## 第三步：功能测试

### 3.1 测试前准备
1. 确保Dr.COM客户端**没有**在运行
2. 确保火绒安全软件已安装
3. 确保网络连接正常

### 3.2 运行完整测试
1. 在工具目录中运行：
   ```
   python main.py --debug
   ```
2. 观察输出，工具会执行以下步骤：
   - 等待系统启动（模拟）
   - 关闭浏览器窗口（如果有）
   - 检测网络状态
   - 根据网络状态执行相应操作

### 3.3 分模块测试（可选）

#### 测试网页关闭功能
1. 手动打开一个浏览器，访问校园网登录页面
2. 运行测试：
   ```python
   python -c "from browser_closer import BrowserCloser; c = BrowserCloser(); print('有浏览器打开:', c.is_browser_open())"
   ```

#### 测试网络检测
```python
python -c "from network_checker import NetworkMonitor; m = NetworkMonitor(); print('网络状态:', m.get_network_status())"
```

#### 测试修复工具查找
```python
python -c "from repair_tool import RepairExecutor; r = RepairExecutor(); tool = r.find_repair_tool(); print('找到修复工具:', tool)"
```

#### 测试Dr.COM客户端检测
```python
python -c "from login_automation import DrComAutomator; d = DrComAutomator(); print('客户端运行:', d.is_client_running())"
```

### 3.4 测试登录功能
1. 确保Dr.COM客户端已关闭
2. 运行工具：
   ```
   python main.py
   ```
3. 观察工具是否能够：
   - 自动启动Dr.COM客户端
   - 自动输入账号密码
   - 成功登录

4. **重要**：第一次运行时，请守在电脑前观察：
   - 如果登录失败，工具会显示错误信息
   - 可能需要调整Dr.COM客户端的窗口识别设置

## 第四步：实际使用

### 4.1 常规使用
1. 每次开机后，工具会自动运行（如果设置了开机启动）
2. 或者手动运行：
   ```
   python main.py
   ```

### 4.2 设置开机自启动（重要！）

#### 方法一：使用Windows计划任务（推荐）
1. 按`Win+R`，输入`taskschd.msc`，回车
2. 点击右侧"创建基本任务"
3. 按以下步骤设置：
   - **名称**：`校园网自动登录`
   - **触发器**：`计算机启动时`
   - **操作**：`启动程序`
   - **程序或脚本**：浏览选择`python.exe`（在Python安装目录）
   - **添加参数**：`"完整路径\main.py"`（例如：`"D:\program\AI_practice\auto_logo_in\auto_login_tool\main.py"`）
   - **起始于**：工具目录路径（例如：`D:\program\AI_practice\auto_logo_in\auto_login_tool`）
   - **完成创建**

4. **高级设置**（右键任务→属性）：
   - **常规**：勾选"不管用户是否登录都要运行"和"使用最高权限运行"
   - **条件**：取消"只有在计算机使用交流电源时才启动此任务"
   - **设置**：勾选"如果任务运行时间超过以下时间，停止任务"，设置为`5分钟`

#### 方法二：使用启动文件夹（简单）
1. 创建`main.py`的快捷方式
2. 按`Win+R`，输入`shell:startup`，回车
3. 将快捷方式复制到打开的启动文件夹中
4. **注意**：此方法需要用户登录后才运行

### 4.3 验证开机启动
1. 重启计算机
2. 观察工具是否自动运行
3. 检查日志文件：`auto_login_tool\logs\campus_auto_login_YYYY-MM-DD.log`
4. 检查开机日志：`auto_login_tool\logs\startup.log`

## 第五步：故障排除

### 5.1 常见问题及解决方案

#### 问题1：找不到火绒修复工具
**症状**：日志显示"未找到火绒修复工具"
**解决**：
1. 确认火绒安全软件已安装
2. 检查`config.ini`中的`huorong_path`是否正确
3. 手动查找火绒修复工具：
   - 打开火绒安装目录
   - 查找类似`hrfix.exe`、`hrnetfix.exe`的文件
   - 如果找到，更新配置文件中的路径

#### 问题2：无法自动登录Dr.COM客户端
**症状**：工具运行但Dr.COM客户端未登录
**解决**：
1. 使用调试模式运行：`python main.py --debug`
2. 查看详细日志，确定失败原因
3. 可能的原因和解决方案：
   - **窗口识别失败**：Dr.COM客户端窗口标题可能不同
     - 修改`login_automation.py`中的`window_titles`列表
     - 添加实际的窗口标题
   - **控件识别失败**：使用备用登录方法
     - 工具内置4种登录方法，会自动尝试
   - **路径错误**：确认`drcom_path`配置正确

#### 问题3：网络检测不准确
**症状**：工具误判网络状态
**解决**：
1. 检查防火墙设置，确保允许Python访问网络
2. 修改`network_checker.py`中的检测目标：
   - 将`ping_targets`和`http_targets`改为更稳定的地址
   - 例如使用校园网内的检测地址

#### 问题4：Windows通知不显示
**症状**：工具运行成功但没有弹出通知
**解决**：
1. 检查Windows通知设置：
   - 设置 → 系统 → 通知和操作
   - 确保通知已开启
2. 检查`config.ini`中的`enable_notifications`是否为`true`

### 5.2 日志分析
1. 日志文件位置：`auto_login_tool\logs\`
2. 主要日志文件：
   - `campus_auto_login_YYYY-MM-DD.log`：日常运行日志
   - `startup.log`：开机启动日志
3. 查看日志方法：
   ```
   python main.py --debug  # 控制台显示详细日志
   ```
   或直接打开日志文件查看

### 5.3 获取帮助
1. 查看详细帮助：
   ```
   python main.py --help
   ```
2. 运行测试模式：
   ```
   python main.py --test
   ```
3. 重新运行设置向导：
   ```
   python main.py --setup
   ```

## 第六步：高级配置

### 6.1 自定义配置
编辑`config.ini`文件可以调整以下设置：

```ini
[settings]
startup_delay = 30          ; 开机后等待时间（秒）
retry_count = 3             ; 登录重试次数
retry_interval = 10         ; 重试间隔（秒）
network_timeout = 10        ; 网络检测超时（秒）
repair_timeout = 60         ; 修复工具超时（秒）
enable_notifications = true ; 是否启用通知
log_level = INFO           ; 日志级别：DEBUG, INFO, WARNING, ERROR

[browser]
browser_keywords = 校园网,登录,Dr.COM,认证  ; 浏览器窗口识别关键词
close_method = alt_f4      ; 关闭方法：alt_f4, ctrl_w, kill_process
close_delay = 2            ; 关闭前等待时间（秒）
```

### 6.2 调试技巧
1. **启用调试日志**：
   - 修改`config.ini`中的`log_level = DEBUG`
   - 或运行`python main.py --debug`

2. **保存调试信息**：
   ```
   python main.py --debug > debug_log.txt 2>&1
   ```

3. **检查特定模块**：
   每个模块都有测试函数，可以直接运行测试：
   ```
   python -c "import browser_closer; browser_closer.test_browser_closer()"
   ```

## 第七步：维护和更新

### 7.1 定期检查
1. 每月检查一次日志文件大小
2. 清理旧日志（工具会自动清理7天前的日志）
3. 确认配置仍然有效

### 7.2 更新工具
1. 如果有新版本，下载更新文件
2. 备份`config.ini`文件
3. 替换其他文件
4. 恢复`config.ini`文件
5. 测试工具是否正常工作

### 7.3 卸载工具
1. 删除工具目录
2. 删除计划任务（如果设置了）
3. 从启动文件夹删除快捷方式（如果设置了）
4. 删除日志目录（可选）

## 注意事项

1. **安全提醒**：
   - 工具会存储您的校园网密码，请妥善保管配置文件
   - 建议使用Windows凭据管理器存储密码
   - 不要将`config.ini`文件分享给他人

2. **使用合规**：
   - 请确保您有权使用自动登录功能
   - 遵守校园网使用规定

3. **技术支持**：
   - 遇到问题时，首先查看日志文件
   - 使用调试模式获取更多信息
   - 如果无法解决，保存日志文件寻求帮助

## 紧急情况处理

如果工具出现问题导致无法上网：

1. **手动登录**：直接打开Dr.COM客户端手动登录
2. **禁用工具**：暂时重命名或移动工具目录
3. **使用火绒修复**：手动运行火绒的网络修复工具
4. **检查网络设置**：使用Windows网络故障排除

---

**祝您使用愉快！如果遇到问题，请参考本指南的故障排除部分。**