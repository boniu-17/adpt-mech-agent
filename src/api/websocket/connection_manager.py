"""
WebSocket连接管理器
管理活跃的WebSocket连接
"""

import asyncio
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """连接WebSocket"""
        await websocket.accept()
        async with self._lock:
            self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session: {session_id}")
    
    async def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        async with self._lock:
            if session_id in self.active_connections:
                del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected for session: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """向指定会话发送消息"""
        async with self._lock:
            if session_id in self.active_connections:
                try:
                    await self.active_connections[session_id].send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to {session_id}: {e}")
                    # 连接可能已断开，移除它
                    await self.disconnect(session_id)
    
    async def broadcast(self, message: dict, exclude_sessions: Set[str] = None):
        """广播消息到所有连接"""
        if exclude_sessions is None:
            exclude_sessions = set()
        
        async with self._lock:
            disconnected = []
            for session_id, websocket in self.active_connections.items():
                if session_id not in exclude_sessions:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {session_id}: {e}")
                        disconnected.append(session_id)
            
            # 清理断开的连接
            for session_id in disconnected:
                await self.disconnect(session_id)
    
    def is_connected(self, session_id: str) -> bool:
        """检查会话是否连接"""
        return session_id in self.active_connections
    
    def get_connected_sessions(self) -> Set[str]:
        """获取所有连接的会话ID"""
        return set(self.active_connections.keys())