"""
数据库工具模块 - Redis相关工具函数
"""

import os

# Redis相关工具函数
import redis.asyncio as redis
import yaml


class RedisConfig:
    """Redis配置类"""

    def __init__(self):
        # 读取配置文件
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        config_path = os.path.join(project_root, 'configs', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        redis_config = config.get('redis', {})
        self.host = redis_config.get('host', 'localhost')
        self.port = redis_config.get('port', 6379)
        self.db = redis_config.get('db', 0)
        self.password = redis_config.get('password')
        self.ssl = redis_config.get('ssl', False)
        self.socket_timeout = redis_config.get('socket_timeout', 5)
        self.socket_connect_timeout = redis_config.get('socket_connect_timeout', 5)
        self.retry_on_timeout = redis_config.get('retry_on_timeout', True)
        self.connection_pool_size = redis_config.get('connection_pool_size', 10)


async def get_redis_client() -> redis.Redis:
    """获取Redis客户端"""
    config = RedisConfig()

    connection_params = {
        'host': config.host,
        'port': config.port,
        'db': config.db,
        'ssl': config.ssl,
        'socket_timeout': config.socket_timeout,
        'socket_connect_timeout': config.socket_connect_timeout,
        'retry_on_timeout': config.retry_on_timeout,
        'max_connections': config.connection_pool_size
    }

    if config.password:
        connection_params['password'] = config.password

    client = redis.Redis(**connection_params)

    # 测试连接
    try:
        await client.ping()
        print(f"✅ Redis连接成功: {config.host}:{config.port}")
    except Exception as e:
        raise ConnectionError(f"Redis连接失败: {e}")

    return client
