"""
数据库工具
提供数据库连接和会话管理的工具函数
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import yaml
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class DatabaseConfig:
    """数据库配置类"""

    def __init__(self):
        # 读取配置文件
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        config_path = os.path.join(project_root, 'configs', 'config.yaml')

        # 如果找不到配置文件，尝试相对路径
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'configs',
                                       'config.yaml')

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        db_config = config.get('database', {})
        self.dialect = db_config.get('dialect', 'mysql')
        self.host = db_config.get('host', 'localhost')
        self.port = db_config.get('port', 3306)
        self.database = db_config.get('database', 'agent_config_center')
        self.username = db_config.get('username', 'root')
        self.password = db_config.get('password', '')
        self.pool_size = db_config.get('pool_size', 5)
        self.max_overflow = db_config.get('max_overflow', 10)
        self.echo = db_config.get('echo', False)


class DatabaseManager:
    """数据库管理器"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._setup_engine()

    def _setup_engine(self):
        """设置数据库引擎"""
        config = DatabaseConfig()

        # 构建数据库URL
        if config.dialect == 'mysql':
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(config.password)
            db_url = f"mysql+aiomysql://{config.username}:{encoded_password}@{config.host}:{config.port}/{config.database}"
        elif config.dialect == 'sqlite':
            db_url = f"sqlite+aiosqlite:///{config.database}.db"
        else:
            raise ValueError(f"不支持的数据库方言: {config.dialect}")

        # 创建异步引擎
        self._engine = create_async_engine(
            db_url,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            echo=config.echo,
            pool_pre_ping=True,
            pool_recycle=3600,
            future=True
        )

        # 创建会话工厂
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话（只提供会话）"""
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取带事务的数据库会话"""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def get_engine(self):
        """获取数据库引擎"""
        return self._engine

    async def close(self):
        """关闭数据库连接"""
        if self._engine:
            await self._engine.dispose()


# 全局数据库管理器实例
_db_manager = DatabaseManager()


@asynccontextmanager
async def get_async_session(with_transaction: bool = True) -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话

    Args:
        with_transaction: 是否自动管理事务，默认为 True
                         True: 自动提交/回滚
                         False: 手动管理事务
    """
    if with_transaction:
        async with _db_manager.get_transaction_session() as session:
            yield session
    else:
        async with _db_manager.get_session() as session:
            yield session


async def close_database():
    """关闭数据库连接"""
    await _db_manager.close()
