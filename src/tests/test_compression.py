#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试压缩备份功能
用于验证压缩备份是否正常工作
"""

import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime

def create_test_files(test_dir):
    """创建测试文件"""
    # 创建测试目录结构
    os.makedirs(os.path.join(test_dir, "subdir1"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "subdir2"), exist_ok=True)
    
    # 创建测试文件
    test_files = [
        "file1.txt",
        "file2.txt", 
        "subdir1/file3.txt",
        "subdir1/file4.txt",
        "subdir2/file5.txt"
    ]
    
    for file_path in test_files:
        full_path = os.path.join(test_dir, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件 {file_path} 的内容\n")
            f.write(f"创建时间: {datetime.now().isoformat()}\n")
    
    print(f"创建测试文件完成: {test_dir}")

def test_compression():
    """测试压缩功能"""
    print("=== 压缩备份功能测试 ===\n")
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_source = os.path.join(temp_dir, "test_source")
        test_backup = os.path.join(temp_dir, "test_backup")
        
        os.makedirs(test_source, exist_ok=True)
        os.makedirs(test_backup, exist_ok=True)
        
        # 创建测试文件
        create_test_files(test_source)
        
        # 测试不同压缩级别
        compression_levels = [1, 6, 9]
        
        for level in compression_levels:
            print(f"测试压缩级别 {level}:")
            
            # 创建压缩备份
            backup_path = os.path.join(test_backup, f"test_backup_level_{level}.zip")
            
            try:
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=level) as zipf:
                    for root, dirs, files in os.walk(test_source):
                        # 跳过隐藏文件和系统文件
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        
                        for file in files:
                            if not file.startswith('.'):
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, test_source)
                                zipf.write(file_path, arcname)
                
                # 添加元数据
                backup_info = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d_%H%M"),
                    'created_at': datetime.now().isoformat(),
                    'type': 'test',
                    'source_directory': test_source,
                    'compressed': True,
                    'compression_level': level
                }
                
                with zipfile.ZipFile(backup_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                    metadata_json = json.dumps(backup_info, ensure_ascii=False, indent=2)
                    zipf.writestr('backup_info.json', metadata_json)
                
                # 获取文件大小
                original_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                  for dirpath, dirnames, filenames in os.walk(test_source)
                                  for filename in filenames)
                compressed_size = os.path.getsize(backup_path)
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                print(f"  原始大小: {original_size:,} 字节")
                print(f"  压缩大小: {compressed_size:,} 字节")
                print(f"  压缩率: {compression_ratio:.1f}%")
                
                # 验证压缩包内容
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    print(f"  包含文件数: {len(file_list)}")
                    
                    # 检查元数据文件
                    if 'backup_info.json' in file_list:
                        info_json = zipf.read('backup_info.json').decode('utf-8')
                        info = json.loads(info_json)
                        print(f"  元数据验证: ✓ (压缩级别={info.get('compression_level')})")
                    else:
                        print(f"  元数据验证: ✗")
                
                print()
                
            except Exception as e:
                print(f"  压缩失败: {str(e)}\n")

def test_metadata_extraction():
    """测试元数据提取"""
    print("=== 元数据提取测试 ===\n")
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_source = os.path.join(temp_dir, "test_source")
        test_backup = os.path.join(temp_dir, "test_backup")
        
        os.makedirs(test_source, exist_ok=True)
        os.makedirs(test_backup, exist_ok=True)
        
        # 创建测试文件
        create_test_files(test_source)
        
        # 创建压缩备份
        backup_path = os.path.join(test_backup, "test_metadata.zip")
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(test_source):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, test_source)
                        zipf.write(file_path, arcname)
        
        # 添加元数据
        backup_info = {
            'timestamp': '2025-01-15_1000',
            'created_at': datetime.now().isoformat(),
            'type': 'hourly',
            'source_directory': test_source,
            'compressed': True,
            'compression_level': 6
        }
        
        with zipfile.ZipFile(backup_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
            metadata_json = json.dumps(backup_info, ensure_ascii=False, indent=2)
            zipf.writestr('backup_info.json', metadata_json)
        
        # 测试元数据提取
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    info_json = zipf.read('backup_info.json').decode('utf-8')
                    info = json.loads(info_json)
                    
                    print("元数据提取成功:")
                    print(f"  时间戳: {info.get('timestamp')}")
                    print(f"  备份类型: {info.get('type')}")
                    print(f"  压缩状态: {info.get('compressed')}")
                    print(f"  压缩级别: {info.get('compression_level')}")
                    print(f"  源目录: {info.get('source_directory')}")
                    print()
                else:
                    print("元数据提取失败: 未找到backup_info.json")
        except Exception as e:
            print(f"元数据提取失败: {str(e)}")

if __name__ == "__main__":
    test_compression()
    test_metadata_extraction()
    
    print("=== 测试完成 ===")
    print("如果所有测试都通过，说明压缩备份功能正常工作。") 