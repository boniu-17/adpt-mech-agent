#!/usr/bin/env python3
"""
测试日志配置脚本
验证日志系统是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.shared.utils.log_config import init_logging, get_log_file_info
import logging


def test_logging():
    """测试日志功能"""
    
    print("=== 测试日志配置 ===")
    
    # 使用配置文件初始化日志
    config_path = "../configs/config.yaml"
    if Path(config_path).exists():
        print(f"使用配置文件: {config_path}")
        init_logging(config_path)
    else:
        print("使用默认日志配置")
        from src.shared.utils.logger import setup_logging
        setup_logging(level="DEBUG", log_file="logs/test.log")
    
    # 获取不同模块的logger进行测试
    logger = logging.getLogger(__name__)
    agent_logger = logging.getLogger("src.agents")
    knowledge_logger = logging.getLogger("src.knowledge")
    service_logger = logging.getLogger("src.services")
    
    # 测试不同级别的日志
    print("\n测试日志级别:")
    logger.debug("这是一条DEBUG级别的消息")
    logger.info("这是一条INFO级别的消息")
    logger.warning("这是一条WARNING级别的消息")
    logger.error("这是一条ERROR级别的消息")
    logger.critical("这是一条CRITICAL级别的消息")
    
    # 测试不同模块的日志
    print("\n测试不同模块的日志:")
    agent_logger.info("智能体模块日志测试")
    knowledge_logger.info("知识库模块日志测试")
    service_logger.info("服务模块日志测试")
    
    # 显示日志文件信息
    print("\n=== 日志文件信息 ===")
    info = get_log_file_info("../logs")
    print(f"总文件数: {info.get('total_files', 0)}")
    print(f"总大小: {info.get('total_size', 0) / 1024:.2f} KB")
    
    if 'files' in info:
        print("文件列表:")
        for file_info in info['files']:
            print(f"  - {file_info['name']}: {file_info['size']} bytes")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_logging()