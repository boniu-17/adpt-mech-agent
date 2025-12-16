"""
主协调器
负责消息路由、Agent调用和流式响应处理
"""

import logging
from typing import Optional, AsyncGenerator
from src.orchestrator.session_manager import SessionManager
from src.services.agent_service import AgentService
from src.api.websocket.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class Orchestrator:
    """主协调器"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        agent_service: AgentService,
        connection_manager: ConnectionManager
    ):
        self.session_manager = session_manager
        self.agent_service = agent_service
        self.connection_manager = connection_manager
    
    async def process_message(
        self,
        session_id: str,
        user_message: str,
        agent_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """处理用户消息并返回流式响应"""
        try:
            # 获取或创建会话
            session = await self.session_manager.get_or_create_session(session_id, agent_id)
            
            # 添加用户消息到会话
            await self.session_manager.add_message(
                session_id=session.id,
                user_message=user_message,
                assistant_response="",  # 先设为空，后面会更新
                user_role="user",
                assistant_role="assistant"
            )
            
            # 获取Agent实例
            agent = await self.agent_service.get_agent(session.agent_id)
            if not agent:
                yield f"Error: Agent {session.agent_id} not found"
                return
            
            # 获取消息历史
            message_history = await self.session_manager.get_message_history(session.id)
            
            # 调用Agent处理消息（流式）
            full_response = ""
            async for chunk in agent.process_message_stream(user_message, message_history):
                full_response += chunk
                yield chunk
                
                # 实时发送到WebSocket
                await self.connection_manager.send_message(
                    session_id=session.id,
                    message={
                        "type": "message_chunk",
                        "content": chunk,
                        "session_id": session.id
                    }
                )
            
            # 更新助手响应
            await self.session_manager.add_message(
                session_id=session.id,
                user_message=user_message,
                assistant_response=full_response,
                user_role="user",
                assistant_role="assistant"
            )
            
            # 发送完成消息
            await self.connection_manager.send_message(
                session_id=session.id,
                message={
                    "type": "message_complete",
                    "content": full_response,
                    "session_id": session.id
                }
            )
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            yield error_msg
            
            # 发送错误消息
            await self.connection_manager.send_message(
                session_id=session_id,
                message={
                    "type": "error",
                    "content": error_msg,
                    "session_id": session_id
                }
            )
    
    async def create_session(self, agent_id: Optional[str] = None) -> str:
        """创建新会话"""
        session = await self.session_manager.create_session(agent_id)
        return session.id
    
    async def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        try:
            # 断开所有相关WebSocket连接
            await self.connection_manager.disconnect(session_id)
            
            # 删除会话
            result = await self.session_manager.delete_session(session_id)
            
            logger.info(f"Session closed: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[dict]:
        """获取会话信息"""
        session = await self.session_manager.get_session(session_id)
        if session:
            return {
                "session_id": session.id,
                "agent_id": session.agent_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": len(session.messages),
                "is_connected": self.connection_manager.is_connected(session_id)
            }
        return None
    
    async def get_active_sessions(self) -> list:
        """获取活跃会话列表"""
        return self.connection_manager.get_connected_sessions()