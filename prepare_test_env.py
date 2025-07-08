#!/usr/bin/env python3
"""
测试环境准备脚本
只负责清理 test 目录、创建源目录、目标目录和一些空的测试文件。
"""
import os
import shutil
from datetime import datetime

def clear_test_directory(test_dir):
    """清除 test 目录下的所有内容"""
    for item in os.listdir(test_dir):
        item_path = os.path.join(test_dir, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"删除失败: {item_path}: {e}")
    print("✓ test 目录清理完成")

def create_directory_structure(test_dir):
    """创建源目录和目标目录及子目录"""
    source_dir = os.path.join(test_dir, 'source')
    target_dir = os.path.join(test_dir, 'target')
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)
    # 子目录
    for sub in ['documents', 'images', 'data', 'config']:
        os.makedirs(os.path.join(source_dir, sub), exist_ok=True)
    for sub in ['hourly', 'daily', 'weekly']:
        os.makedirs(os.path.join(target_dir, sub), exist_ok=True)
    print("✓ 目录结构创建完成")
    return source_dir, target_dir

def create_test_files(source_dir):
    """创建一些空的测试文件"""
    files = [
        ('documents', 'readme.txt'),
        ('documents', 'config.txt'),
        ('images', 'photo1.jpg'),
        ('data', 'database.db'),
        ('config', 'settings.json'),
        ('', 'main.py'),
    ]
    for subdir, filename in files:
        if subdir:
            file_dir = os.path.join(source_dir, subdir)
        else:
            file_dir = source_dir
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('')
    print("✓ 空测试文件创建完成")

def main():
    print("=== 测试环境准备脚本 ===")
    # 获取 test 目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(script_dir, 'test')
    os.makedirs(test_dir, exist_ok=True)
    clear_test_directory(test_dir)
    source_dir, target_dir = create_directory_structure(test_dir)
    create_test_files(source_dir)
    print("=== 测试环境准备完成 ===")

if __name__ == "__main__":
    main() 