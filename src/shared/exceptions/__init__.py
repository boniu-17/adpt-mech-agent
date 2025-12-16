"""
统一异常体系
定义项目使用的所有异常类型
"""

from .base_errors import BaseError, ConfigError, ValidationError, ConfigurationError
from .agent_errors import (
    AgentError,
    AgentExecutionError,
    AgentInitializationError,
    ToolNotFoundError,
    ToolExecutionError,
    LLMError,
    TimeoutError,
    ResourceNotFoundError,
    PermissionError,
    RetryExhaustedError,
    InvalidStateError
)
from .knowledge_errors import (
    KnowledgeBaseError,
    DocumentLoadError,
    EmbeddingError,
    RetrievalError,
    VectorStoreError
)
from .tool_errors import (
    ToolError,
    ToolValidationError,
    ToolTimeoutError,
    ToolPermissionError
)

__all__ = [
    'BaseError',
    'ConfigError',
    'ValidationError',
    'ConfigurationError',
    'AgentError',
    'AgentExecutionError',
    'AgentInitializationError',
    'ToolNotFoundError',
    'ToolExecutionError',
    'LLMError',
    'TimeoutError',
    'ResourceNotFoundError',
    'PermissionError',
    'RetryExhaustedError',
    'InvalidStateError',
    'KnowledgeBaseError',
    'DocumentLoadError',
    'EmbeddingError',
    'RetrievalError',
    'VectorStoreError',
    'ToolError',
    'ToolValidationError',
    'ToolTimeoutError',
    'ToolPermissionError'
]