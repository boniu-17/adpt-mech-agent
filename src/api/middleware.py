"""
中间件模块 - FastAPI自定义中间件
处理请求日志、异常处理、CORS等
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"Request started: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录请求完成
            logger.info(
                f"Request completed: {request.method} {request.url} "
                f"Status: {response.status_code} Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url} "
                f"Error: {str(e)} Time: {process_time:.3f}s"
            )
            raise


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """异常处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled exception in request {request.method} {request.url}: {e}")
            # 这里可以返回统一的错误响应
            raise


def setup_cors_middleware(app):
    """设置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_custom_middleware(app):
    """设置自定义中间件"""
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ExceptionHandlingMiddleware)