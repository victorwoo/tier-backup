#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试备份逻辑脚本
用于验证不同时间点的备份策略判断是否正确
"""

from datetime import datetime, timedelta
import json

def should_create_backup(now):
    """判断指定时间是否需要创建备份"""
    # 每小时备份：每小时都执行
    hourly_backup = True
    
    # 每日备份：每天23:59执行
    daily_backup = now.hour == 23 and now.minute >= 59
    
    # 每周备份：每周日23:55执行
    weekly_backup = now.weekday() == 6 and now.hour == 23 and now.minute >= 55
    
    return {
        'hourly': hourly_backup,
        'daily': daily_backup,
        'weekly': weekly_backup
    }

def test_backup_logic():
    """测试不同时间点的备份逻辑"""
    print("=== 备份策略测试 ===\n")
    
    # 测试时间点
    test_times = [
        datetime.now().replace(hour=10, minute=30, second=0, microsecond=0),  # 普通小时
        datetime.now().replace(hour=23, minute=59, second=30, microsecond=0),  # 每日备份时间
        datetime.now().replace(hour=23, minute=55, second=0, microsecond=0),   # 每周备份时间（如果不是周日）
        datetime.now().replace(hour=23, minute=55, second=0, microsecond=0),   # 每周备份时间（周日）
    ]
    
    # 设置最后一个测试时间为周日
    test_times[3] = test_times[3] + timedelta(days=(6 - test_times[3].weekday()))
    
    for i, test_time in enumerate(test_times, 1):
        result = should_create_backup(test_time)
        
        print(f"测试 {i}: {test_time.strftime('%Y-%m-%d %H:%M:%S')} ({test_time.strftime('%A')})")
        print(f"  每小时备份: {result['hourly']}")
        print(f"  每日备份: {result['daily']}")
        print(f"  每周备份: {result['weekly']}")
        print()

def test_backup_schedule():
    """测试24小时的备份计划"""
    print("=== 24小时备份计划测试 ===\n")
    
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for hour in range(24):
        test_time = base_time + timedelta(hours=hour)
        result = should_create_backup(test_time)
        
        # 只显示有特殊备份的时间点
        if result['daily'] or result['weekly']:
            print(f"{test_time.strftime('%H:%M')} - {test_time.strftime('%A')}")
            if result['daily']:
                print("  ✓ 每日备份")
            if result['weekly']:
                print("  ✓ 每周备份")
            print()

if __name__ == "__main__":
    test_backup_logic()
    test_backup_schedule()
    
    print("=== 当前时间测试 ===")
    now = datetime.now()
    result = should_create_backup(now)
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
    print(f"备份策略: {json.dumps(result, ensure_ascii=False, indent=2)}") 