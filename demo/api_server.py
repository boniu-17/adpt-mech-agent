#!/usr/bin/env python3
"""
Agent Service API Server
为量子销售经理智能体提供Web API接口
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.agent_service import AgentService
from src.managers.agent_manager import AgentManager
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="量子销售经理智能体API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
agent_service = None
agent_manager = None

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    agent_id: str = "quantum_sales_manager"
    session_id: str = None
    stream: bool = True

class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool
    message: str = None
    data: Dict[str, Any] = None
    error: str = None

class AgentInfo(BaseModel):
    """智能体信息模型"""
    id: str
    name: str
    type: str
    description: str
    avatar_url: str = None
    expertise_domains: List[str]
    personality_tags: List[str]
    is_usable: bool

@app.on_event("startup")
async def startup_event():
    """启动时初始化智能体服务"""
    global agent_service, agent_manager
    try:
        logger.info("正在初始化智能体服务...")
        agent_manager = AgentManager()
        agent_service = AgentService(agent_manager)
        
        # 初始化智能体管理器
        await agent_manager.initialize()
        logger.info("智能体管理器初始化成功")
        
    except Exception as e:
        logger.error(f"智能体服务初始化失败: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回Web演示界面"""
    with open("demo/web_demo.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/agents/{agent_id}")
async def get_agent_info(agent_id: str) -> AgentInfo:
    """获取智能体信息"""
    try:
        if not agent_manager:
            raise HTTPException(status_code=503, detail="智能体服务未初始化")
        
        agent = await agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")
        
        # 从配置中提取信息
        config = agent.full_config
        profile = config.agent_profile
        
        return AgentInfo(
            id=agent_id,
            name=profile.display_name,
            type=config.agent_config.agent_type,
            description=config.agent_config.description,
            avatar_url=profile.avatar_url,
            expertise_domains=profile.expertise_domains,
            personality_tags=profile.personality_tags,
            is_usable=profile.is_usable
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取智能体信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取智能体信息失败: {str(e)}")

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """与智能体进行对话（非流式）"""
    try:
        if not agent_service:
            raise HTTPException(status_code=503, detail="智能体服务未初始化")
        
        # 处理消息
        result = await agent_service.process_message(
            agent_id=request.agent_id,
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            success=True,
            message="对话处理成功",
            data={
                "response": result.response,
                "session_id": result.session_id,
                "tokens_used": result.tokens_used,
                "processing_time": result.processing_time
            }
        )
        
    except Exception as e:
        logger.error(f"对话处理失败: {e}")
        return ChatResponse(
            success=False,
            error=f"对话处理失败: {str(e)}"
        )

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket流式对话接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = message_data.get("message", "")
            agent_id = message_data.get("agent_id", "quantum_sales_manager")
            session_id = message_data.get("session_id")
            
            if not message:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "消息不能为空"
                }))
                continue
            
            # 发送开始流式响应信号
            await websocket.send_text(json.dumps({
                "type": "stream_start",
                "session_id": session_id
            }))
            
            # 处理流式响应
            async for chunk in agent_service.process_message_stream(
                agent_id=agent_id,
                message=message,
                session_id=session_id
            ):
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk,
                    "session_id": session_id
                }))
            
            # 发送结束信号
            await websocket.send_text(json.dumps({
                "type": "stream_end",
                "session_id": session_id
            }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket对话处理失败: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"对话处理失败: {str(e)}"
        }))

@app.get("/api/conversations/{session_id}/export")
async def export_conversation(session_id: str):
    """导出对话记录"""
    try:
        if not agent_service:
            raise HTTPException(status_code=503, detail="智能体服务未初始化")
        
        # 获取对话历史
        history = await agent_service.get_conversation_history(session_id)
        
        # 生成Markdown格式的对话记录
        markdown_content = f"# 量子销售经理对话记录\n\n"
        markdown_content += f"**会话ID**: {session_id}\n"
        markdown_content += f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, message in enumerate(history, 1):
            role = "用户" if message.role == "user" else "量子销售经理"
            markdown_content += f"## 第{i}轮对话\n"
            markdown_content += f"**{role}**: {message.content}\n"
            markdown_content += f"**时间**: {message.timestamp}\n\n"
        
        return {
            "success": True,
            "data": {
                "format": "markdown",
                "content": markdown_content,
                "filename": f"quantum_sales_conversation_{session_id}.md"
            }
        }
        
    except Exception as e:
        logger.error(f"导出对话记录失败: {e}")
        return {
            "success": False,
            "error": f"导出失败: {str(e)}"
        }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "quantum_sales_agent_api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)