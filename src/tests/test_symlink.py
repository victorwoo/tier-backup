#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试软链接功能
用于验证软链接备份是否正常工作
"""

import os
import json
import hashlib
import tempfile
import shutil
from datetime import datetime

def calculate_directory_hash(source_dir, max_files=1000):
    """计算目录的哈希值，用于检测文件变化"""
    try:
        hash_md5 = hashlib.md5()
        file_count = 0
        
        for root, dirs, files in os.walk(source_dir):
            # 跳过隐藏文件和系统文件
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information']]
            
            # 按文件名排序，确保哈希值的一致性
            files.sort()
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    # 计算文件的相对路径和修改时间
                    rel_path = os.path.relpath(file_path, source_dir)
                    mtime = os.path.getmtime(file_path)
                    size = os.path.getsize(file_path)
                    
                    # 将文件信息添加到哈希中
                    file_info = f"{rel_path}:{mtime}:{size}"
                    hash_md5.update(file_info.encode('utf-8'))
                    
                    file_count += 1
                    
                    # 限制文件数量，避免计算时间过长
                    if file_count >= max_files:
                        print(f"文件数量超过{max_files}，停止计算哈希")
                        break
                        
                except (OSError, IOError) as e:
                    print(f"无法访问文件 {file_path}: {str(e)}")
                    continue
            
            if file_count >= max_files:
                break
        
        # 添加目录信息到哈希中
        hash_md5.update(f"file_count:{file_count}".encode('utf-8'))
        
        return hash_md5.hexdigest(), file_count
        
    except Exception as e:
        print(f"计算目录哈希失败: {str(e)}")
        return None, 0

def create_test_files(test_dir, content_suffix=""):
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
            f.write(f"这是测试文件 {file_path} 的内容{content_suffix}\n")
            f.write(f"创建时间: {datetime.now().isoformat()}\n")
    
    print(f"创建测试文件完成: {test_dir}")

def test_hash_consistency():
    """测试哈希值的一致性"""
    print("=== 哈希值一致性测试 ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_source")
        os.makedirs(test_dir, exist_ok=True)
        
        # 创建相同的文件两次
        create_test_files(test_dir, "_第一次")
        hash1, count1 = calculate_directory_hash(test_dir)
        print(f"第一次哈希: {hash1[:8]}... (文件数: {count1})")
        
        # 删除文件，重新创建相同内容
        shutil.rmtree(test_dir)
        os.makedirs(test_dir, exist_ok=True)
        create_test_files(test_dir, "_第一次")  # 相同内容
        hash2, count2 = calculate_directory_hash(test_dir)
        print(f"第二次哈希: {hash2[:8]}... (文件数: {count2})")
        
        if hash1 == hash2:
            print("✓ 哈希值一致，测试通过")
        else:
            print("✗ 哈希值不一致，测试失败")
        
        # 修改一个文件
        test_file = os.path.join(test_dir, "file1.txt")
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write("新增内容\n")
        
        hash3, count3 = calculate_directory_hash(test_dir)
        print(f"修改后哈希: {hash3[:8]}... (文件数: {count3})")
        
        if hash3 != hash1:
            print("✓ 文件修改后哈希值变化，测试通过")
        else:
            print("✗ 文件修改后哈希值未变化，测试失败")
        
        print()

def test_symlink_creation():
    """测试软链接创建"""
    print("=== 软链接创建测试 ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建源目录
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        create_test_files(source_dir)
        
        # 创建目标目录
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)
        
        # 创建软链接
        symlink_path = os.path.join(target_dir, "symlink_test")
        try:
            os.symlink(source_dir, symlink_path)
            print(f"✓ 软链接创建成功: {symlink_path} -> {source_dir}")
            
            # 验证软链接
            if os.path.islink(symlink_path):
                print("✓ 软链接验证成功")
                
                # 检查软链接内容
                linked_files = os.listdir(symlink_path)
                print(f"软链接目录包含 {len(linked_files)} 个文件/目录")
                
                # 测试通过软链接访问文件
                test_file = os.path.join(symlink_path, "file1.txt")
                if os.path.exists(test_file):
                    print("✓ 通过软链接访问文件成功")
                else:
                    print("✗ 通过软链接访问文件失败")
            else:
                print("✗ 软链接验证失败")
                
        except Exception as e:
            print(f"✗ 软链接创建失败: {str(e)}")
        
        print()

def test_symlink_backup_simulation():
    """模拟软链接备份过程"""
    print("=== 软链接备份模拟测试 ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建备份目录结构
        backup_dir = os.path.join(temp_dir, "backup")
        hourly_dir = os.path.join(backup_dir, "hourly")
        os.makedirs(hourly_dir, exist_ok=True)
        
        # 创建第一次备份
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        create_test_files(source_dir, "_原始")
        
        # 计算哈希值
        hash1, count1 = calculate_directory_hash(source_dir)
        print(f"原始目录哈希: {hash1[:8]}... (文件数: {count1})")
        
        # 创建第一次备份（模拟实际备份）
        backup1_path = os.path.join(hourly_dir, "2025-01-15_1000")
        shutil.copytree(source_dir, backup1_path)
        
        # 创建备份元数据
        backup_info1 = {
            'timestamp': '2025-01-15_1000',
            'created_at': datetime.now().isoformat(),
            'type': 'hourly',
            'directory_hash': hash1,
            'file_count': count1,
            'is_symlink': False
        }
        
        with open(os.path.join(backup1_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
            json.dump(backup_info1, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 第一次备份创建: {backup1_path}")
        
        # 模拟第二次备份（内容相同）
        hash2, count2 = calculate_directory_hash(source_dir)
        print(f"第二次目录哈希: {hash2[:8]}... (文件数: {count2})")
        
        if hash1 == hash2:
            print("✓ 检测到目录内容未变化，创建软链接备份")
            
            # 创建软链接备份
            backup2_path = os.path.join(hourly_dir, "2025-01-15_1100")
            try:
                os.symlink(backup1_path, backup2_path)
                
                # 创建软链接元数据
                backup_info2 = {
                    'timestamp': '2025-01-15_1100',
                    'created_at': datetime.now().isoformat(),
                    'type': 'hourly',
                    'is_symlink': True,
                    'symlink_target': backup1_path
                }
                
                with open(os.path.join(backup2_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                    json.dump(backup_info2, f, ensure_ascii=False, indent=2)
                
                print(f"✓ 软链接备份创建: {backup2_path} -> {backup1_path}")
                
                # 验证软链接
                if os.path.islink(backup2_path):
                    print("✓ 软链接验证成功")
                    
                    # 检查软链接指向的内容
                    linked_content = os.listdir(backup2_path)
                    print(f"软链接目录包含 {len(linked_content)} 个文件/目录")
                else:
                    print("✗ 软链接验证失败")
                    
            except Exception as e:
                print(f"✗ 软链接备份创建失败: {str(e)}")
        else:
            print("✗ 哈希值不一致，不应该创建软链接")
        
        print()

def test_system_symlink_support():
    """测试系统是否支持软链接"""
    print("=== 系统软链接支持测试 ===\n")
    
    try:
        # 尝试创建软链接
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            
            symlink_file = os.path.join(temp_dir, "symlink.txt")
            os.symlink(test_file, symlink_file)
            
            if os.path.islink(symlink_file):
                print("✓ 系统支持软链接")
                return True
            else:
                print("✗ 系统不支持软链接")
                return False
                
    except Exception as e:
        print(f"✗ 系统不支持软链接: {str(e)}")
        return False

if __name__ == "__main__":
    print("软链接功能测试开始\n")
    
    # 测试系统支持
    if not test_system_symlink_support():
        print("系统不支持软链接，跳过其他测试")
        exit(1)
    
    # 运行其他测试
    test_hash_consistency()
    test_symlink_creation()
    test_symlink_backup_simulation()
    
    print("=== 测试完成 ===")
    print("如果所有测试都通过，说明软链接功能正常工作。") 