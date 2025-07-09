#!/bin/bash

# macOS/Linux 备份脚本启动器
# 使用方法: ./run_backup.sh

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到项目根目录
cd "$SCRIPT_DIR/.."

# 检查 Python 是否可用
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "错误: 未找到 Python 解释器"
    echo "请安装 Python 3: https://www.python.org/downloads/"
    exit 1
fi

# 检查 rsync 是否可用
if ! command -v rsync &> /dev/null; then
    echo "错误: 未找到 rsync 命令"
    echo "macOS 通常内置 rsync，如果缺失请安装: brew install rsync"
    exit 1
fi

# 检查配置文件是否存在
if [ ! -f "config/back_config.json" ]; then
    echo "错误: 未找到 config/back_config.json 配置文件"
    echo "请参考 config/config_examples.json 创建配置文件"
    exit 1
fi

# 运行备份脚本
echo "启动备份脚本..."
echo "Python 版本: $($PYTHON_CMD --version)"
echo "rsync 版本: $(rsync --version | head -n1)"
echo "当前时间: $(date)"
echo "----------------------------------------"

$PYTHON_CMD tier_backup.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "备份脚本执行完成"
else
    echo "----------------------------------------"
    echo "备份脚本执行失败，请检查 backup.log 文件"
    exit 1
fi 