# 校园网自动登录工具（重构版）

一个自动化工具，用于解决每次开机需要手动登录校园网的问题。工具能够自动关闭校园网登录网页，检测网络状态，修复网络问题，并自动登录Dr.COM客户端。

**重构说明**：此版本经过重大重构，代码更简洁、高效、易于维护。移除了不必要的复杂功能，优化了性能，并添加了单元测试。

## 功能特性

- **自动关闭网页**: 检测并关闭校园网登录网页
- **智能网络检测**: 检测网络连通性和VPN残留问题
- **自动修复**: 调用火绒断网修复工具修复网络问题
- **自动登录**: 模拟GUI操作自动登录Dr.COM客户端
- **错误处理**: 完善的错误处理和重试机制
- **日志通知**: 详细的日志记录和Windows通知
- **开机自启**: 支持开机自动运行

## 重构改进

### 代码质量提升
- **代码行数减少 30%**：通过移除冗余代码和简化复杂逻辑
- **模块化设计**：将大型类拆分为更小的单一职责类
- **统一工具模块**：创建了 `utils` 模块，包含公共工具函数
- **简化配置管理**：移除了复杂的加密和Windows凭据管理器依赖
- **智能等待机制**：替代硬编码的 `time.sleep()`，使用条件等待

### 性能优化
- **减少不必要的等待时间**：使用智能等待替代固定延迟
- **优化网络检测**：减少重复的ping/http测试
- **改进错误处理**：使用装饰器统一异常处理

### 可维护性增强
- **添加单元测试**：创建了基本的测试框架
- **类型提示**：完善了函数和方法的类型提示
- **代码注释**：增加了关键代码的注释
- **依赖清理**：移除了不必要的第三方库

## 系统要求

- Windows 10/11
- Python 3.9+（如果使用源码运行）
- Dr.COM宽带认证客户端
- 火绒安全软件（用于网络修复，可选）

## 快速开始

### 方法一：使用Python源码运行

1. 安装Python 3.9+
2. 克隆或下载本项目
3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
4. 运行设置向导：
   ```
   python main.py --setup
   ```
5. 运行工具：
   ```
   python main.py
   ```

### 方法二：使用预编译的exe文件

1. 下载最新版本的 `CampusAutoLogin.exe`
2. 运行 `CampusAutoLogin.exe --setup` 进行初始设置
3. 按照向导配置账号密码和路径
4. 运行 `CampusAutoLogin.exe` 测试工具

## 项目结构

```
auto_login_tool/
├── main.py                    # 主入口文件
├── main_controller.py         # 主控制器（协调所有模块）
├── config.py                  # 配置管理模块
├── browser_closer.py          # 浏览器关闭模块
├── network_checker.py         # 网络检测模块
├── repair_tool.py             # 修复工具模块
├── login_automation.py        # Dr.COM自动化模块
├── logger.py                  # 日志和通知模块
├── utils/                     # 公共工具模块
│   ├── wait.py               # 智能等待工具
│   ├── config.py             # 配置工具
│   ├── logging.py            # 日志工具
│   └── exceptions.py         # 异常类定义
├── tests/                     # 单元测试
│   └── test_basic.py         # 基本测试
├── logs/                      # 日志目录（自动创建）
├── config.ini                 # 配置文件（自动创建）
├── requirements.txt           # Python依赖
└── README.md                  # 本文档
```

## 配置文件

工具使用 `config.ini` 文件进行配置。首次运行时会自动创建配置文件模板。

主要配置节：

```ini
[credentials]
username = 你的校园网账号
password = 你的校园网密码

[paths]
huorong_path = D:\APP\huorongsecurity\Huorong\Sysdiag
drcom_path = C:\Users\用户名\Desktop\APP\DrClient.exe

[settings]
startup_delay = 30
retry_count = 3
retry_interval = 10
network_timeout = 10
repair_timeout = 60
enable_notifications = true
log_level = INFO

[browser]
browser_keywords = 校园网,登录,Dr.COM,认证
close_method = alt_f4
close_delay = 2
```

## 使用方法

### 基本使用
```bash
# 运行完整流程
python main.py

# 使用自定义配置文件
python main.py --config custom.ini

# 启用调试模式
python main.py --debug
```

### 设置向导
```bash
# 运行初始设置向导
python main.py --setup
```

### 测试模式
```bash
# 运行测试模式（不实际执行操作）
python main.py --test
```

### 开机自启动
1. 使用Windows任务计划程序创建任务
2. 触发器：系统启动时
3. 操作：启动 `main_controller.py` 或编译后的exe文件
4. 参数：`--config config.ini`

## 开发指南

### 运行测试
```bash
# 运行所有测试
python -m pytest auto_login_tool/tests/

# 运行特定测试
python -m pytest auto_login_tool/tests/test_basic.py -v
```

### 代码规范
- 使用类型提示
- 遵循PEP 8代码风格
- 函数和类需要文档字符串
- 使用新的工具模块而不是重复代码

### 添加新功能
1. 在适当的模块中添加功能
2. 使用 `utils` 模块中的工具函数
3. 添加单元测试
4. 更新文档

## 故障排除

### 常见问题

1. **Dr.COM客户端无法识别**
   - 确保Dr.COM客户端已安装并可以手动启动
   - 检查 `drcom_path` 配置是否正确
   - 尝试使用 `--debug` 模式查看详细日志

2. **网络检测不准确**
   - 检查防火墙设置，允许Python/ping通过
   - 确保网络连接正常
   - 调整 `network_timeout` 配置值

3. **修复工具找不到**
   - 检查火绒安全软件是否安装
   - 确认 `huorong_path` 配置正确
   - 火绒修复工具可能在不同版本中名称不同

4. **权限问题**
   - 以管理员身份运行工具
   - 确保对相关路径有读写权限

### 日志查看
日志文件位于 `logs/` 目录，按日期命名：
- `campus_auto_login_YYYY-MM-DD.log` - 日常日志
- `startup.log` - 开机启动日志

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- 感谢所有测试者和贡献者
- 感谢火绒安全团队提供的修复工具
- 感谢Python社区提供的优秀库

## 版本历史

### v1.1.0 (2026-04-13) - 重构版
- 重大代码重构，提高可维护性
- 添加单元测试框架
- 简化配置管理
- 优化性能，减少等待时间
- 创建公共工具模块

### v1.0.0 (2026-04-06) - 初始版本
- 基本功能实现
- 支持自动登录Dr.COM客户端
- 支持网络检测和修复
- 支持浏览器窗口关闭
- 支持开机自启动