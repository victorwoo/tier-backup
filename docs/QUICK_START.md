# 快速启动指南

## 系统要求

### Windows

- Windows 10 或更高版本
- robocopy 命令（Windows 内置）
- Python 3.7 或更高版本

### macOS

- macOS 10.14 或更高版本
- rsync 命令（macOS 内置）
- Python 3.7 或更高版本

### Linux

- 大多数 Linux 发行版
- rsync 命令（通常需要安装：`sudo apt-get install rsync` 或 `sudo yum install rsync`）
- Python 3.7 或更高版本

## 1. 创建配置文件

创建 `back_config.json` 文件：

### Windows 示例

```json
{
  "source_directory": "C:\\Users\\YourUsername\\Documents",
  "target_directory": "D:\\Backups",
  "compress_backup": false,
  "compression_level": 6,
  "enable_symlink": true,
  "max_disk_usage_percent": 85
}
```

### macOS 示例

```json
{
  "source_directory": "/Users/YourUsername/Documents",
  "target_directory": "/Volumes/BackupDisk/Backups",
  "compress_backup": false,
  "compression_level": 6,
  "enable_symlink": true,
  "max_disk_usage_percent": 85
}
```

### Linux 示例

```json
{
  "source_directory": "/home/YourUsername/Documents",
  "target_directory": "/mnt/backup/Backups",
  "compress_backup": false,
  "compression_level": 6,
  "enable_symlink": true,
  "max_disk_usage_percent": 85
}
```

## 2. 运行备份

### Windows

```bash
python tier_backup.py
# 或使用脚本
scripts/run_backup.bat
```

### macOS/Linux

```bash
python3 tier_backup.py
# 或使用脚本
./scripts/run_backup.sh
```

## 3. 设置定时任务

### Windows (任务计划程序)

1. 打开任务计划程序
2. 创建基本任务
3. 设置触发器为每小时运行
4. 设置操作为启动程序：`C:\path\to\tier-backup\scripts\run_backup.bat`

### macOS (crontab)

```bash
# 编辑 crontab
crontab -e

# 添加每小时运行的任务
0 * * * * /path/to/tier-backup/scripts/run_backup.sh
```

### Linux (crontab)

```bash
# 编辑 crontab
crontab -e

# 添加每小时运行的任务
0 * * * * /path/to/tier-backup/scripts/run_backup.sh
```

## 4. 验证备份

检查备份目录结构：

```
Backups/
├── hourly/
│   ├── 2024-01-15_1400/
│   └── 2024-01-15_1500/
├── daily/
│   ├── 2024-01-15/
│   └── 2024-01-16/
└── weekly/
    ├── 2024-01-14/
    └── 2024-01-21/
```

## 故障排除

### Windows

- 查看robocopy返回码（0-7表示成功）
- 检查日志文件 `backup.log`
- 确保以管理员权限运行（软链接功能需要）

### macOS/Linux

- 确保 rsync 已安装：`which rsync`
- 检查日志文件 `backup.log`
- 验证文件权限和磁盘空间
- 确保脚本有执行权限：`chmod +x scripts/run_backup.sh`
