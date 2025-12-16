"""
智能体管理相关端点
提供智能体的创建、消息发送等接口
"""
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.services.agent_service import AgentService, get_agent_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


class CreateAgentRequest(BaseModel):
    """创建智能体请求模型"""
    agent_config_id: int = 1  # 默认使用量子销售经理配置


class SendMessageRequest(BaseModel):
    """发送消息请求模型"""
    message: str
    session_id: Optional[str] = None


class APIResponse(BaseModel):
    """API响应模型"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@router.post("/create", response_model=APIResponse)
async def create_agent(
        request: CreateAgentRequest,
        agent_service: AgentService = Depends(get_agent_service)
):
    """创建新的智能体实例"""
    try:
        # 从数据库创建智能体
        agent_id = await agent_service.create_agent_from_db(request.agent_config_id)
        agent = await agent_service.get_agent(agent_id)
        # 重新加载配置以确保获取最新数据
        await agent_service.agent_manager._load_agent_configs()
        cfgs = agent_service.agent_manager.get_all_config()
        all_cfg = cfgs.get(agent_id)
        await agent.initialize(all_cfg)
        return APIResponse(
            success=True,
            data={
                "id": agent_id,
                "name": "量子销售经理",
                "type": "simple",
                "description": "量子销售经理智能体"
            }
        )

    except Exception as e:
        logger.error(f"创建智能体失败: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/{agent_id}/message", response_model=APIResponse)
async def send_message(
        agent_id: str,
        request: SendMessageRequest,
        agent_service: AgentService = Depends(get_agent_service)
):
    """发送消息（非流式）"""
    try:
        result = await agent_service.process_message(
            agent_id=agent_id,
            message=request.message,
            session_id=request.session_id
        )

        return APIResponse(
            success=True,
            data={
                "response": result.response,
                "session_id": result.session_id,
                "processing_time": result.processing_time
            }
        )

    except Exception as e:
        logger.error(f"处理消息失败: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.post("/{agent_id}/stream")
async def stream_message(
        agent_id: str,
        request: SendMessageRequest,
        agent_service: AgentService = Depends(get_agent_service)
):
    """流式聊天接口"""

    async def generate_stream():
        """生成流式响应"""
        try:
            # 发送流开始事件
            yield f"data: {json.dumps({'type': 'stream_start', 'session_id': request.session_id or 'new_session'})}\n\n"

            # 流式处理消息
            full_response = ""
            async for chunk in agent_service.process_message_stream(
                    agent_id=agent_id,
                    message=request.message,
                    session_id=request.session_id
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            # 发送流结束事件
            yield f"data: {json.dumps({'type': 'stream_end', 'session_id': request.session_id or 'new_session'})}\n\n"

        except Exception as e:
            logger.error(f"流式聊天错误: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


@router.get("/{agent_id}/info", response_model=APIResponse)
async def get_agent_info(
        agent_id: str,
        agent_service: AgentService = Depends(get_agent_service)
):
    """获取智能体信息"""
    try:
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="智能体不存在")

        config = agent_service.get_agent_config(agent_id)

        return APIResponse(
            success=True,
            data={
                "id": agent_id,
                "name": config.name if config else "未知",
                "type": config.agent_type if config else "unknown",
                "description": config.description if config else "",
                "status": "active"
            }
        )

    except Exception as e:
        logger.error(f"获取智能体信息失败: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )


@router.get("/list", response_model=APIResponse)
async def list_agents(
        agent_service: AgentService = Depends(get_agent_service)
):
    """列出所有智能体ID"""
    try:
        agent_ids = agent_service.list_agents()

        return APIResponse(
            success=True,
            data={
                "agents": agent_ids
            }
        )

    except Exception as e:
        logger.error(f"列出智能体失败: {e}")
        return APIResponse(
            success=False,
            error=str(e)
        )
