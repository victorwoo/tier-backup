#!/usr/bin/env python3
"""
Tier Backup - 智能分层备份解决方案
主入口文件
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.tier_backup import main

if __name__ == '__main__':
    # 默认配置文件路径
    config_file = os.path.join('config', 'back_config.json')
    
    # 如果命令行提供了配置文件路径，则使用提供的路径
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    main(config_file) 