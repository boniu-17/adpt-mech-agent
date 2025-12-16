"""
API路由配置
注册所有API路由
"""

from fastapi import APIRouter
from src.api.v1.endpoints import chat, agents

# 创建主路由器
api_router = APIRouter()

# 注册路由
api_router.include_router(chat.router, prefix="")
api_router.include_router(agents.router, prefix="")