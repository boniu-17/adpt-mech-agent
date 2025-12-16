"""
日志配置模块
提供基于配置文件的日志系统初始化功能
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import TimedRotatingFileHandler

from .logger import setup_logging, ColoredFormatter


def setup_logging_from_config(config: Dict[str, Any]) -> None:
    """
    根据配置文件设置日志系统
    
    Args:
        config: 日志配置字典
    """
    if not config:
        # 使用默认配置
        setup_logging()
        return
    
    log_config = config.get('logging', {})
    
    # 基础配置
    level = log_config.get('level', 'INFO')
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
    enable_colors = log_config.get('enable_colors', True)
    
    # 文件日志配置
    file_config = log_config.get('file_logging', {})
    console_config = log_config.get('console_logging', {})
    
    # 创建logs目录
    logs_dir = file_config.get('directory', 'logs')
    if file_config.get('enabled', False):
        Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置根日志级别
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # 控制台处理器
    if console_config.get('enabled', True):
        console_handler = logging.StreamHandler()
        console_level = console_config.get('level', level)
        console_numeric_level = getattr(logging, console_level.upper(), numeric_level)
        console_handler.setLevel(console_numeric_level)
        
        if enable_colors:
            formatter = ColoredFormatter(format_str, datefmt=date_format)
        else:
            formatter = logging.Formatter(format_str, datefmt=date_format)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    if file_config.get('enabled', False):
        filename = file_config.get('filename', 'adpt_mech_agent.log')
        log_file = Path(logs_dir) / filename
        
        max_bytes = file_config.get('max_bytes', 10485760)  # 10MB
        backup_count = file_config.get('backup_count', 30)
        encoding = file_config.get('encoding', 'utf-8')
        
        # 使用TimedRotatingFileHandler实现按时间轮转
        rotation_config = log_config.get('rotation', {})
        when = rotation_config.get('when', 'midnight')
        interval = rotation_config.get('interval', 1)
        rotation_backup_count = rotation_config.get('backup_count', 30)
        
        file_handler = TimedRotatingFileHandler(
            log_file,
            when=when,
            interval=interval,
            backupCount=rotation_backup_count,
            encoding=encoding
        )
        
        file_formatter = logging.Formatter(format_str, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 设置特定模块的日志级别
    loggers_config = log_config.get('loggers', {})
    for logger_name, logger_level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        numeric_logger_level = getattr(logging, logger_level.upper(), numeric_level)
        logger.setLevel(numeric_logger_level)
    
    # 防止日志传播到父logger
    root_logger.propagate = False
    
    logging.info(f"日志系统已初始化 - 级别: {level}, 文件日志: {'启用' if file_config.get('enabled') else '禁用'}")


def cleanup_old_logs(logs_dir: str, days_to_keep: int = 30) -> None:
    """
    清理旧的日志文件
    
    Args:
        logs_dir: 日志目录路径
        days_to_keep: 保留天数
    """
    try:
        from datetime import datetime, timedelta
        import glob
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        log_files = glob.glob(os.path.join(logs_dir, "*.log*"))
        
        deleted_count = 0
        for log_file in log_files:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                deleted_count += 1
        
        if deleted_count > 0:
            logging.info(f"清理了 {deleted_count} 个超过 {days_to_keep} 天的旧日志文件")
            
    except Exception as e:
        logging.warning(f"清理旧日志文件时出错: {e}")


def get_log_file_info(logs_dir: str = "logs") -> Dict[str, Any]:
    """
    获取日志文件信息
    
    Args:
        logs_dir: 日志目录路径
        
    Returns:
        包含日志文件信息的字典
    """
    try:
        import glob
        import os
        
        log_files = glob.glob(os.path.join(logs_dir, "*.log*"))
        
        info = {
            "total_files": len(log_files),
            "files": [],
            "total_size": 0
        }
        
        for log_file in log_files:
            file_stat = os.stat(log_file)
            info["files"].append({
                "name": os.path.basename(log_file),
                "size": file_stat.st_size,
                "modified": file_stat.st_mtime
            })
            info["total_size"] += file_stat.st_size
        
        return info
        
    except Exception as e:
        logging.error(f"获取日志文件信息时出错: {e}")
        return {"error": str(e)}


# 便捷函数
def init_logging(config_path: Optional[str] = None) -> None:
    """
    初始化日志系统
    
    Args:
        config_path: 配置文件路径
    """
    config = {}
    
    if config_path and Path(config_path).exists():
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    setup_logging_from_config(config)