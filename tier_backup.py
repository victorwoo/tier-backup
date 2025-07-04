import os
import shutil
import json
import time
import logging
import zipfile
import hashlib
from datetime import datetime, timedelta
import re

# 配置日志
logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config():
    """加载配置文件"""
    try:
        with open('back_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        raise

def should_create_backup():
    """判断当前是否需要创建备份"""
    now = datetime.now()
    
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
                        logging.warning(f"文件数量超过{max_files}，停止计算哈希")
                        break
                        
                except (OSError, IOError) as e:
                    logging.warning(f"无法访问文件 {file_path}: {str(e)}")
                    continue
            
            if file_count >= max_files:
                break
        
        # 添加目录信息到哈希中
        hash_md5.update(f"file_count:{file_count}".encode('utf-8'))
        
        return hash_md5.hexdigest(), file_count
        
    except Exception as e:
        logging.error(f"计算目录哈希失败: {str(e)}")
        return None, 0

def get_last_backup_info(backup_dir, backup_type):
    """获取最后一次备份的信息"""
    try:
        type_dir = os.path.join(backup_dir, backup_type)
        if not os.path.exists(type_dir):
            return None
        
        backups = []
        for item in os.listdir(type_dir):
            item_path = os.path.join(type_dir, item)
            
            if os.path.isdir(item_path):
                # 目录备份
                info_file = os.path.join(item_path, 'backup_info.json')
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                            if info.get('type') == backup_type:
                                backups.append({
                                    'path': item_path,
                                    'timestamp': info.get('timestamp', ''),
                                    'created_at': info.get('created_at', ''),
                                    'compressed': False,
                                    'hash': info.get('directory_hash', ''),
                                    'is_symlink': os.path.islink(item_path)
                                })
                    except Exception as e:
                        logging.warning(f"读取备份信息失败: {item_path}, 错误: {str(e)}")
                        continue
            elif item.endswith('.zip'):
                # 压缩备份
                try:
                    with zipfile.ZipFile(item_path, 'r') as zipf:
                        if 'backup_info.json' in zipf.namelist():
                            info_json = zipf.read('backup_info.json').decode('utf-8')
                            info = json.loads(info_json)
                            if info.get('type') == backup_type:
                                backups.append({
                                    'path': item_path,
                                    'timestamp': info.get('timestamp', ''),
                                    'created_at': info.get('created_at', ''),
                                    'compressed': True,
                                    'hash': info.get('directory_hash', ''),
                                    'is_symlink': os.path.islink(item_path)
                                })
                except Exception as e:
                    logging.warning(f"读取压缩备份信息失败: {item_path}, 错误: {str(e)}")
                    continue
        
        # 按时间排序，获取最新的备份
        if backups:
            backups.sort(key=lambda x: x['created_at'])
            return backups[-1]
        
        return None
        
    except Exception as e:
        logging.error(f"获取最后备份信息失败: {str(e)}")
        return None

def create_symlink_backup(target_path, source_path, backup_type, timestamp, compress=False):
    """创建软链接备份"""
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 创建软链接
        if os.path.exists(target_path):
            if os.path.islink(target_path):
                os.unlink(target_path)
            elif os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        
        # 创建软链接
        os.symlink(source_path, target_path)
        
        # 创建元数据文件
        backup_info = {
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'type': backup_type,
            'source_directory': source_path,
            'compressed': compress,
            'is_symlink': True,
            'symlink_target': source_path
        }
        
        if compress:
            # 压缩备份的软链接，将元数据添加到ZIP文件中
            with zipfile.ZipFile(target_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                metadata_json = json.dumps(backup_info, ensure_ascii=False, indent=2)
                zipf.writestr('backup_info.json', metadata_json)
        else:
            # 目录备份的软链接，创建元数据文件
            with open(os.path.join(target_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
        
        logging.info(f"创建软链接备份: {target_path} -> {source_path}")
        return target_path
        
    except Exception as e:
        logging.error(f"创建软链接备份失败: {str(e)}")
        return None

def create_compressed_backup(source_dir, backup_path, compression_level=6):
    """创建压缩备份"""
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            for root, dirs, files in os.walk(source_dir):
                # 跳过隐藏文件和系统文件
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information']]
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        # 计算相对路径
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        logging.debug(f"添加文件到压缩包: {arcname}")
        
        logging.info(f"压缩备份创建成功: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"创建压缩备份失败: {str(e)}")
        return False

def create_backup(source_dir, target_base_dir, backup_type, compress=False, compression_level=6, enable_symlink=True):
    """创建新备份"""
    if not os.path.exists(source_dir):
        logging.error(f"源目录不存在: {source_dir}")
        return None
    
    # 根据备份类型创建不同的目录结构
    now = datetime.now()
    
    if backup_type == 'hourly':
        # 每小时备份：YYYY-MM-DD_HHMM 格式
        timestamp = now.strftime("%Y-%m-%d_%H%M")
        backup_dir = os.path.join(target_base_dir, 'hourly', timestamp)
    elif backup_type == 'daily':
        # 每日备份：YYYY-MM-DD 格式
        timestamp = now.strftime("%Y-%m-%d")
        backup_dir = os.path.join(target_base_dir, 'daily', timestamp)
    elif backup_type == 'weekly':
        # 每周备份：YYYY-MM-DD 格式（周日）
        timestamp = now.strftime("%Y-%m-%d")
        backup_dir = os.path.join(target_base_dir, 'weekly', timestamp)
    else:
        logging.error(f"未知的备份类型: {backup_type}")
        return None
    
    # 确保目标目录存在
    os.makedirs(os.path.dirname(backup_dir), exist_ok=True)
    
    try:
        # 检查是否启用软链接功能
        if enable_symlink:
            # 计算当前目录的哈希值
            current_hash, file_count = calculate_directory_hash(source_dir)
            if current_hash:
                logging.info(f"当前目录哈希: {current_hash[:8]}... (文件数: {file_count})")
                
                # 获取最后一次备份信息
                last_backup = get_last_backup_info(target_base_dir, backup_type)
                if last_backup and last_backup.get('hash') == current_hash:
                    logging.info(f"检测到目录内容未变化，创建软链接备份")
                    
                    # 创建软链接备份
                    backup_path = backup_dir + ('.zip' if compress else '')
                    return create_symlink_backup(backup_path, last_backup['path'], backup_type, timestamp, compress)
        
        # 创建实际备份
        if compress:
            # 创建压缩备份
            backup_path = backup_dir + '.zip'
            success = create_compressed_backup(source_dir, backup_path, compression_level)
            if not success:
                return None
        else:
            # 创建目录备份
            backup_path = backup_dir
            # 使用robocopy进行高效复制（Windows系统）
            cmd = f'robocopy "{source_dir}" "{backup_path}" /MIR /Z /COPY:DAT /R:3 /W:10 /NFL /NDL'
            result = os.system(cmd)
            
            # robocopy返回码：0-7表示成功，8及以上表示错误
            if result > 7:
                logging.error(f"{backup_type}备份失败，robocopy返回码: {result}")
                return None
        
        # 计算目录哈希值
        directory_hash, file_count = calculate_directory_hash(source_dir)
        
        # 添加备份元数据文件
        backup_info = {
            'timestamp': timestamp,
            'created_at': now.isoformat(),
            'type': backup_type,
            'source_directory': source_dir,
            'compressed': compress,
            'compression_level': compression_level if compress else None,
            'directory_hash': directory_hash,
            'file_count': file_count,
            'is_symlink': False
        }
        
        # 如果是压缩备份，将元数据文件添加到压缩包中
        if compress:
            with zipfile.ZipFile(backup_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                # 创建元数据JSON字符串
                metadata_json = json.dumps(backup_info, ensure_ascii=False, indent=2)
                zipf.writestr('backup_info.json', metadata_json)
        else:
            # 目录备份，创建元数据文件
            with open(os.path.join(backup_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
                
        logging.info(f"{backup_type}备份成功: {backup_path}")
        return backup_path
            
    except Exception as e:
        logging.error(f"{backup_type}备份失败: {str(e)}")
        return None

def get_backups_by_type(backup_dir):
    """按类型获取备份"""
    backups = {
        'hourly': [],
        'daily': [],
        'weekly': []
    }
    
    for backup_type in backups.keys():
        type_dir = os.path.join(backup_dir, backup_type)
        if not os.path.exists(type_dir):
            continue
            
        for item in os.listdir(type_dir):
            item_path = os.path.join(type_dir, item)
            
            # 检查是否为目录或压缩文件
            if os.path.isdir(item_path):
                # 目录备份
                info_file = os.path.join(item_path, 'backup_info.json')
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                            if info.get('type') == backup_type:
                                backups[backup_type].append({
                                    'path': item_path,
                                    'timestamp': info.get('timestamp', ''),
                                    'created_at': info.get('created_at', ''),
                                    'compressed': False,
                                    'is_symlink': info.get('is_symlink', False),
                                    'hash': info.get('directory_hash', '')
                                })
                    except Exception as e:
                        logging.warning(f"读取备份信息失败: {item_path}, 错误: {str(e)}")
                        continue
            elif item.endswith('.zip'):
                # 压缩备份
                try:
                    with zipfile.ZipFile(item_path, 'r') as zipf:
                        if 'backup_info.json' in zipf.namelist():
                            info_json = zipf.read('backup_info.json').decode('utf-8')
                            info = json.loads(info_json)
                            if info.get('type') == backup_type:
                                backups[backup_type].append({
                                    'path': item_path,
                                    'timestamp': info.get('timestamp', ''),
                                    'created_at': info.get('created_at', ''),
                                    'compressed': True,
                                    'is_symlink': info.get('is_symlink', False),
                                    'hash': info.get('directory_hash', '')
                                })
                except Exception as e:
                    logging.warning(f"读取压缩备份信息失败: {item_path}, 错误: {str(e)}")
                    continue
    
    # 按时间排序（旧到新）
    for backup_type in backups.keys():
        backups[backup_type].sort(key=lambda x: x['timestamp'])
    
    return backups

def cleanup_old_backups(config, backup_dir):
    """清理旧备份"""
    backups = get_backups_by_type(backup_dir)
    
    # 清理每小时备份：保留最近24个
    if len(backups['hourly']) > 24:
        for old_backup in backups['hourly'][:-24]:
            delete_backup(old_backup['path'])
            logging.info(f"删除过期每小时备份: {old_backup['timestamp']}")
    
    # 清理每日备份：保留最近30个
    if len(backups['daily']) > 30:
        for old_backup in backups['daily'][:-30]:
            delete_backup(old_backup['path'])
            logging.info(f"删除过期每日备份: {old_backup['timestamp']}")
    
    # 清理每周备份：保留最近52个（约一年）
    if len(backups['weekly']) > 52:
        for old_backup in backups['weekly'][:-52]:
            delete_backup(old_backup['path'])
            logging.info(f"删除过期每周备份: {old_backup['timestamp']}")
    
    # 检查磁盘空间，必要时删除最旧的备份
    check_disk_space_and_cleanup(config, backup_dir)

def delete_backup(backup_path):
    """删除指定备份"""
    try:
        if os.path.exists(backup_path):
            if os.path.islink(backup_path):
                # 删除软链接
                os.unlink(backup_path)
            elif os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)
            logging.info(f"删除备份: {backup_path}")
    except Exception as e:
        logging.error(f"删除备份失败: {backup_path}, 错误: {str(e)}")

def check_disk_space_and_cleanup(config, backup_dir):
    """检查磁盘空间并清理"""
    try:
        # 获取磁盘使用情况
        total, used, free = shutil.disk_usage(backup_dir)
        max_usage_percent = config.get('max_disk_usage_percent', 85)
        current_usage_percent = (used / total) * 100
        
        logging.info(f"磁盘使用情况: {current_usage_percent:.2f}%, 最大允许: {max_usage_percent}%")
        
        # 如果磁盘使用率超过限制，开始清理
        if current_usage_percent > max_usage_percent:
            logging.warning(f"磁盘空间不足，开始清理...")
            
            # 获取所有备份并按时间排序
            all_backups = []
            backups = get_backups_by_type(backup_dir)
            
            # 按优先级排序：先删除每小时备份，再删除每日备份，最后删除每周备份
            for backup_type in ['hourly', 'daily', 'weekly']:
                all_backups.extend(backups[backup_type])
            
            # 按创建时间排序（旧到新）
            all_backups.sort(key=lambda x: x['created_at'])
            
            # 逐个删除最旧的备份，直到空间足够
            for backup in all_backups:
                delete_backup(backup['path'])
                total, used, free = shutil.disk_usage(backup_dir)
                current_usage_percent = (used / total) * 100
                
                if current_usage_percent <= max_usage_percent - 5:  # 留出一些缓冲空间
                    logging.info(f"磁盘空间清理完成，当前使用率: {current_usage_percent:.2f}%")
                    break
    except Exception as e:
        logging.error(f"检查磁盘空间失败: {str(e)}")

def main():
    """主函数"""
    try:
        logging.info("=== 备份脚本启动 ===")
        config = load_config()
        
        source_dir = config.get('source_directory', '')
        target_dir = config.get('target_directory', '')
        compress = config.get('compress_backup', False)
        compression_level = config.get('compression_level', 6)
        enable_symlink = config.get('enable_symlink', True)
        
        if not source_dir or not target_dir:
            logging.error("源目录或目标目录未配置")
            return
        
        logging.info(f"备份配置: 压缩={compress}, 压缩级别={compression_level}, 软链接={enable_symlink}")
        
        # 判断需要执行的备份类型
        backup_types = should_create_backup()
        logging.info(f"备份策略判断结果: {backup_types}")
        
        # 执行相应的备份
        created_backups = []
        for backup_type, should_backup in backup_types.items():
            if should_backup:
                backup_path = create_backup(source_dir, target_dir, backup_type, compress, compression_level, enable_symlink)
                if backup_path:
                    created_backups.append(backup_type)
        
        # 如果有备份创建成功，执行清理
        if created_backups:
            cleanup_old_backups(config, target_dir)
            logging.info(f"成功创建备份类型: {', '.join(created_backups)}")
        else:
            logging.info("当前时间无需创建备份")
        
        logging.info("=== 备份脚本执行完成 ===")
    except Exception as e:
        logging.critical(f"备份脚本运行失败: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()    