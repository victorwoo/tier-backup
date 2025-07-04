# 快速开始指南

## 1. 下载和配置

1. 将所有文件下载到同一个目录（如 `D:\backup`）
2. 编辑 `back_config.json`，设置源目录和目标目录：
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

### 备份模式选择

**目录备份模式（默认）：**
- 设置 `"compress_backup": false`
- 直接复制文件，访问速度快
- 适合频繁访问的备份

**压缩备份模式：**
- 设置 `"compress_backup": true`
- 创建ZIP压缩包，节省磁盘空间
- 适合长期存储

**软链接备份模式：**
- 设置 `"enable_symlink": true`
- 当目录内容未变化时创建软链接
- 极大节省磁盘空间和时间

**压缩级别设置：**
- 1-3：快速压缩，适合大文件
- 4-6：平衡模式（推荐）
- 7-9：高压缩率，适合小文件

## 2. 测试脚本

双击 `run_backup.bat` 或在命令行运行：
```bash
python tier_backup.py
```

## 3. 设置计划任务

在 Windows 任务计划程序中创建新任务：

**基本设置：**
- 名称：智能备份任务
- 描述：每小时执行智能备份

**触发器：**
- 新建触发器
- 开始任务：按计划
- 设置：每天
- 重复任务间隔：1小时
- 持续时间：无限期

**操作：**
- 程序/脚本：`D:\backup\run_backup.bat`
- 起始于：`D:\backup`

**条件：**
- 勾选"只有在计算机使用交流电源时才启动此任务"
- 勾选"如果计算机切换到电池电源，则停止任务"

**重要：** 如果启用软链接功能，需要以管理员身份运行任务计划程序。

## 4. 验证运行

1. 检查 `backup.log` 文件确认脚本正常运行
2. 查看备份目录结构是否正确创建
3. 等待到23:59和周日23:55验证每日和每周备份

## 5. 备份策略说明

- **每小时备份**：每小时执行，保留24个
- **每日备份**：每天23:59执行，保留30个  
- **每周备份**：每周日23:55执行，保留52个

脚本会自动判断当前时间并执行相应的备份策略。

## 6. 功能优势

### 压缩备份优势
启用压缩备份可以：
- 节省50-80%的磁盘空间
- 减少备份时间（网络传输）
- 提高备份安全性（文件完整性）
- 支持更高的保留数量

### 软链接备份优势
启用软链接备份可以：
- 节省90%以上的磁盘空间（当内容未变化时）
- 几乎瞬间完成备份
- 自动检测文件变化
- 保持完整的备份历史记录

**注意事项：**
- 压缩过程会消耗更多CPU资源
- 解压需要额外时间
- 建议在系统负载较低时使用高压缩级别
- Windows需要管理员权限才能创建软链接
- 软链接指向的原始备份被删除后，软链接将失效 