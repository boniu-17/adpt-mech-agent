#!/usr/bin/env python3
"""
测试缓存修复脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.managers.cache_manager import get_cache_manager

async def test_cache_pattern():
    """测试缓存模式匹配"""
    cache_manager = get_cache_manager()
    
    # 创建一个测试配置
    test_config = {
        "agent_config": {
            "name": "test_agent",
            "agent_type": "simple"
        },
        "agent_profile": {
            "display_name": "测试智能体"
        }
    }
    
    # 保存一个测试配置
    agent_id = "agent_simple_test_agent_1234567890"
    await cache_manager.set_config("agent", agent_id, test_config)
    print(f"✅ 已保存测试配置: {agent_id}")
    
    # 测试获取所有agent配置
    try:
        all_configs = await cache_manager.get_all_config("agent", "*")
        print(f"✅ 获取到的配置数量: {len(all_configs)}")
        for key, config in all_configs.items():
            print(f"   - {key}: {config}")
    except Exception as e:
        print(f"❌ 获取配置失败: {e}")
    
    # 清理测试数据
    await cache_manager.delete_config("agent", agent_id)
    print("✅ 清理测试数据完成")

if __name__ == "__main__":
    asyncio.run(test_cache_pattern())