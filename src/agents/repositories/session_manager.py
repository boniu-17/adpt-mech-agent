"""
数据库会话管理器
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.utils.db_utils import _db_manager


class SessionManager:
    """数据库会话管理器"""

    def __init__(self, session_factory: Optional[Callable] = None):
        self.session_factory = session_factory or _db_manager.get_transaction_session
        self._current_session: Optional[AsyncSession] = None

    @asynccontextmanager
    async def get_session(self, with_transaction: bool = True) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话

        Args:
            with_transaction: 是否自动管理事务
        """
        if with_transaction:
            async with self.session_factory() as session:
                self._current_session = session
                try:
                    yield session
                finally:
                    self._current_session = None
        else:
            async with self.session_factory(with_transaction=False) as session:
                self._current_session = session
                try:
                    yield session
                finally:
                    self._current_session = None

    def get_current_session(self) -> Optional[AsyncSession]:
        """获取当前会话（如果有）"""
        return self._current_session


# 全局会话管理器实例
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """获取会话管理器实例"""
    return _session_manager
