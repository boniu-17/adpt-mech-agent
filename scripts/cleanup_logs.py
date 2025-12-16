#!/usr/bin/env python3
"""
日志清理脚本
用于定期清理超过指定天数的旧日志文件
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.shared.utils.log_config import cleanup_old_logs, get_log_file_info


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理旧的日志文件')
    parser.add_argument('--logs-dir', '-d', default='logs', 
                       help='日志目录路径 (默认: logs)')
    parser.add_argument('--days-to-keep', '-k', type=int, default=30,
                       help='保留天数 (默认: 30)')
    parser.add_argument('--dry-run', action='store_true',
                       help='模拟运行，不实际删除文件')
    parser.add_argument('--info', action='store_true',
                       help='显示日志文件信息')
    
    args = parser.parse_args()
    
    # 显示日志文件信息
    if args.info:
        info = get_log_file_info(args.logs_dir)
        print(f"日志目录: {args.logs_dir}")
        print(f"总文件数: {info.get('total_files', 0)}")
        print(f"总大小: {info.get('total_size', 0) / 1024 / 1024:.2f} MB")
        
        if 'files' in info:
            print("\n文件列表:")
            for file_info in info['files']:
                print(f"  - {file_info['name']}: {file_info['size'] / 1024:.2f} KB")
        return
    
    # 检查日志目录是否存在
    logs_path = Path(args.logs_dir)
    if not logs_path.exists():
        print(f"日志目录不存在: {args.logs_dir}")
        return
    
    # 模拟运行
    if args.dry_run:
        print(f"模拟清理日志 (保留最近 {args.days_to_keep} 天的文件):")
        print(f"日志目录: {args.logs_dir}")
        
        info = get_log_file_info(args.logs_dir)
        print(f"当前文件数: {info.get('total_files', 0)}")
        print(f"当前大小: {info.get('total_size', 0) / 1024 / 1024:.2f} MB")
        
        print("\n此操作将删除超过指定天数的日志文件")
        return
    
    # 执行清理
    print(f"开始清理超过 {args.days_to_keep} 天的旧日志文件...")
    print(f"日志目录: {args.logs_dir}")
    
    try:
        # 先显示清理前的信息
        info_before = get_log_file_info(args.logs_dir)
        print(f"清理前文件数: {info_before.get('total_files', 0)}")
        print(f"清理前大小: {info_before.get('total_size', 0) / 1024 / 1024:.2f} MB")
        
        # 执行清理
        cleanup_old_logs(args.logs_dir, args.days_to_keep)
        
        # 显示清理后的信息
        info_after = get_log_file_info(args.logs_dir)
        print(f"清理后文件数: {info_after.get('total_files', 0)}")
        print(f"清理后大小: {info_after.get('total_size', 0) / 1024 / 1024:.2f} MB")
        
        deleted_count = info_before.get('total_files', 0) - info_after.get('total_files', 0)
        freed_space = (info_before.get('total_size', 0) - info_after.get('total_size', 0)) / 1024 / 1024
        
        print(f"\n清理完成! 删除了 {deleted_count} 个文件，释放了 {freed_space:.2f} MB 空间")
        
    except Exception as e:
        print(f"清理过程中出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()