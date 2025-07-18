# tier-backup

智能分层备份解决方案

## 一、概述

本脚本实现了智能分层备份策略，能够自动判断并执行不同类型的备份：

**备份策略：**

- **每小时备份**：每小时执行一次，保留最近24个备份
- **每日备份**：每天23:59执行，保留最近30个备份  
- **每周备份**：每周日23:55执行，保留最近52个备份（约一年）

**智能特性：**

- 只需设置一个每小时执行的计划任务
- 脚本自动判断当前时间是否需要执行每日或每周备份
- 当磁盘空间不足时，按优先级自动清理旧备份（每小时→每日→每周）
- **支持压缩备份**：可选择创建ZIP压缩包以节省磁盘空间
- **支持软链接备份**：当目录内容未变化时，创建软链接而不是重复备份

## 二、项目结构

```
tier-backup/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   └── tier_backup.py # 主备份逻辑
│   ├── utils/             # 工具函数模块
│   └── tests/             # 测试模块
├── config/                # 配置文件目录
│   ├── back_config.json   # 主配置文件
│   └── config_examples.json # 配置示例
├── scripts/               # 脚本文件目录
│   ├── run_backup.bat     # Windows启动脚本
│   └── run_backup.sh      # Linux/macOS启动脚本
├── docs/                  # 文档目录
├── examples/              # 示例文件目录
├── tier_backup.py         # 主入口文件
├── pyproject.toml         # Python项目配置
├── Makefile              # 构建和开发工具
└── backup.log            # 日志文件
```

详细的项目结构说明请参考：[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 三、配置说明

编辑 `config/back_config.json` 文件，设置以下参数：

**Windows 示例：**

```json
{
    "source_directory": "C:\\Users\\YourUsername\\Documents",
    "target_directory": "D:\\Backups",
    "max_disk_usage_percent": 85,
    "log_level": "INFO",
    "compress_backup": false,
    "compression_level": 6,
    "enable_symlink": true
}
```

**macOS/Linux 示例：**

```json
{
    "source_directory": "/Users/YourUsername/Documents",
    "target_directory": "/Volumes/BackupDisk/Backups",
    "max_disk_usage_percent": 85,
    "log_level": "INFO",
    "compress_backup": false,
    "compression_level": 6,
    "enable_symlink": true
}
```

参数说明：

- `source_directory`：需要备份的源目录路径
- `target_directory`：备份文件存储的目标路径
- `max_disk_usage_percent`：磁盘最大使用率阈值（超过此值自动清理旧备份）
- `log_level`：日志级别（DEBUG/INFO/WARNING/ERROR）
- `compress_backup`：是否启用压缩备份（true/false）
- `compression_level`：压缩级别（1-9，1最快但压缩率最低，9最慢但压缩率最高）
- `enable_symlink`：是否启用软链接功能（true/false）

## 四、备份模式

### 1. 目录备份模式（默认）

- 直接复制源目录到目标位置
- 保持原始文件结构
- 访问速度快，便于浏览

### 2. 压缩备份模式

- 将源目录压缩为ZIP文件
- 显著节省磁盘空间
- 支持不同压缩级别
- 元数据信息存储在ZIP包内

### 3. 软链接备份模式

- 当检测到目录内容未变化时，创建软链接
- 极大节省磁盘空间和时间
- 自动计算目录哈希值进行变化检测
- 支持目录和压缩备份的软链接

**软链接工作原理：**

1. 计算当前目录的MD5哈希值（基于文件路径、修改时间、大小）
2. 与最后一次备份的哈希值比较
3. 如果哈希值相同，创建软链接指向最后一次实际备份
4. 如果哈希值不同，创建新的实际备份

## 五、安装步骤

1. **安装 Python**：确保系统已安装 Python 3.7 或更高版本
2. **安装系统依赖**：
   - Windows：robocopy（系统内置）
   - macOS：rsync（系统内置）
   - Linux：`sudo apt-get install rsync` 或 `sudo yum install rsync`
3. **克隆项目**：`git clone https://github.com/victorwoo/tier-backup.git`
4. **安装依赖**：`pip install -e .` 或 `make install`
5. **配置参数**：修改 `config/back_config.json` 中的源目录和目标目录
6. **选择备份模式**：设置 `compress_backup` 和 `enable_symlink` 参数
7. **测试运行**：`make backup` 或 `python tier_backup.py`

**快速开始：**

```bash
# 克隆项目
git clone https://github.com/victorwoo/tier-backup.git
cd tier-backup

# 安装开发环境
make install

# 配置备份参数
cp config/config_examples.json config/back_config.json
# 编辑 config/back_config.json

# 运行备份
make backup

# 或使用脚本启动
./scripts/run_backup.sh  # macOS/Linux
scripts/run_backup.bat   # Windows
```

## 六、计划任务设置（简化版）

**只需要创建一个计划任务：**

### Windows 系统

- **触发器**：每天，每小时，持续执行
- **操作**：启动程序 `D:\tier-backup\scripts\run_backup.bat`
- **参数**：无（脚本会自动判断备份类型）

### macOS/Linux 系统

- **触发器**：每天，每小时，持续执行
- **操作**：启动程序 `/path/to/tier-backup/scripts/run_backup.sh`
- **参数**：无（脚本会自动判断备份类型）

**脚本会自动判断：**

- 每小时都执行每小时备份
- 每天23:59执行每日备份
- 每周日23:55执行每周备份

## 七、备份文件结构

### 目录备份模式

```
backup/
├── hourly/
│   ├── 2025-01-15_0900/
│   │   ├── [源文件]
│   │   └── backup_info.json
│   └── ...
├── daily/
│   ├── 2025-01-15/
│   │   ├── [源文件]
│   │   └── backup_info.json
│   └── ...
└── weekly/
    ├── 2025-01-12/
    │   ├── [源文件]
    │   └── backup_info.json
    └── ...
```

### 压缩备份模式

```
backup/
├── hourly/
│   ├── 2025-01-15_0900.zip
│   └── ...
├── daily/
│   ├── 2025-01-15.zip
│   └── ...
└── weekly/
    ├── 2025-01-12.zip
    └── ...
```

### 软链接备份模式

```
backup/
├── hourly/
│   ├── 2025-01-15_0900/          # 实际备份
│   ├── 2025-01-15_1000 -> 2025-01-15_0900/  # 软链接
│   └── ...
```

每个备份都包含：

- 完整的源文件副本（或软链接）
- `backup_info.json` 元数据文件（包含备份类型、时间、压缩信息、哈希值等）

## 八、日志查看

所有操作都会记录到 `backup.log` 文件中，示例日志格式：

```
2025-01-15 10:00:01 - INFO - === 备份脚本启动 ===
2025-01-15 10:00:01 - INFO - 备份配置: 压缩=true, 压缩级别=6, 软链接=true
2025-01-15 10:00:02 - INFO - 当前目录哈希: 6bd51663... (文件数: 5)
2025-01-15 10:00:02 - INFO - 检测到目录内容未变化，创建软链接备份
2025-01-15 10:00:02 - INFO - 创建软链接备份: D:\backup\hourly\2025-01-15_1000 -> D:\backup\hourly\2025-01-15_0900
2025-01-15 10:00:02 - INFO - hourly备份成功: D:\backup\hourly\2025-01-15_1000
2025-01-15 10:00:02 - INFO - 成功创建备份类型: hourly
2025-01-15 10:00:02 - INFO - === 备份脚本执行完成 ===
```

## 九、智能清理策略

脚本采用智能清理策略：

1. **按数量清理**：
   - 每小时备份：保留最近24个
   - 每日备份：保留最近30个
   - 每周备份：保留最近52个

2. **按磁盘空间清理**：
   - 当磁盘使用率超过设定阈值时自动清理
   - 按优先级删除：每小时备份 → 每日备份 → 每周备份
   - 保留5%的缓冲空间

3. **软链接优势**：
   - 极大节省磁盘空间（软链接几乎不占用空间）
   - 显著减少备份时间
   - 自动检测文件变化
   - 支持跨文件系统的软链接

## 十、故障排除

1. **脚本不运行**：
   - 检查 Python 路径是否正确
   - 查看 `backup.log` 中的错误信息
   - 确保批处理文件编码为UTF-8

2. **备份不完整**：
   - 确保源目录路径正确且有读取权限
   - 检查目标磁盘空间是否充足
   - Windows：查看robocopy返回码（0-7表示成功）
   - macOS/Linux：查看rsync返回码（0表示成功）

3. **压缩备份失败**：
   - 检查源目录是否包含特殊字符
   - 确保有足够的临时空间进行压缩
   - 尝试降低压缩级别

4. **软链接失败**：
   - 检查系统是否支持软链接（Windows需要管理员权限）
   - 确保目标文件系统支持软链接
   - 检查文件权限

5. **计划任务未触发**：
   - 在任务计划程序中查看历史记录
   - 确保任务设置了正确的用户权限
   - 检查批处理文件路径是否正确

## 十一、注意事项

1. 首次运行会创建所有必要的目录结构
2. 建议将备份目标设置在非系统盘上
3. 定期检查日志文件，确保备份正常进行
4. 脚本会自动处理时区问题，使用系统本地时间
5. 备份元数据文件使用UTF-8编码，支持中文路径
6. **压缩备份注意事项**：
   - 压缩过程会消耗更多CPU资源
   - 压缩时间与文件大小和压缩级别成正比
   - 建议在系统负载较低时使用高压缩级别
7. **软链接注意事项**：
   - Windows需要管理员权限才能创建软链接
   - macOS/Linux默认支持软链接，无需特殊权限
   - 软链接指向的原始备份被删除后，软链接将失效
   - 建议定期验证软链接的有效性

## 十二、高级配置

如需修改备份策略，可以编辑 `tier_backup.py` 中的 `should_create_backup()` 函数：

```python
def should_create_backup():
    now = datetime.now()
    
    # 修改备份时间策略
    hourly_backup = True  # 每小时都执行
    daily_backup = now.hour == 23 and now.minute >= 59  # 每天23:59
    weekly_backup = now.weekday() == 6 and now.hour == 23 and now.minute >= 55  # 每周日23:55
    
    return {
        'hourly': hourly_backup,
        'daily': daily_backup,
        'weekly': weekly_backup
    }
```

如需修改保留策略，可以编辑 `cleanup_old_backups()` 函数中的保留数量。

## 十三、性能建议

1. **目录备份**：适合频繁访问的备份，I/O性能好
2. **压缩备份**：适合长期存储，节省空间
3. **软链接备份**：适合内容变化较少的目录，极大节省空间和时间
4. **压缩级别选择**：
   - 大文件（>1GB）：使用级别1-3
   - 小文件（<100MB）：使用级别7-9
   - 一般文件：使用级别4-6（默认）

## 十四、系统要求

- **操作系统**：Windows 7/8/10/11, Linux, macOS
- **Python版本**：3.7或更高版本
- **备份工具**：
  - Windows：robocopy（系统内置）
  - macOS：rsync（系统内置）
  - Linux：rsync（需要安装：`sudo apt-get install rsync` 或 `sudo yum install rsync`）
- **软链接支持**：
  - Windows：需要管理员权限
  - Linux/macOS：默认支持
- **磁盘空间**：建议至少是源目录大小的2倍
