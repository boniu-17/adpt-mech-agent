"""
智能体相关异常
定义智能体执行过程中的异常类型
"""

from typing import Optional, Dict, Any

from .base_errors import BaseError


class AgentError(BaseError):
    """智能体基础异常"""

    def __init__(
            self,
            message: str,
            agent_name: Optional[str] = None,
            agent_type: Optional[str] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if agent_name:
            details['agent_name'] = agent_name
        if agent_type:
            details['agent_type'] = agent_type

        super().__init__(message, code="AGENT_ERROR", details=details, **kwargs)


class AgentExecutionError(AgentError):
    """智能体执行异常"""

    def __init__(
            self,
            message: str,
            step: Optional[str] = None,
            input_data: Optional[Any] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if step:
            details['step'] = step
        if input_data is not None:
            details['input_data'] = input_data

        super().__init__(message, code="AGENT_EXECUTION_ERROR", details=details, **kwargs)


class AgentInitializationError(AgentError):
    """智能体初始化异常"""

    def __init__(
            self,
            message: str,
            config: Optional[Dict[str, Any]] = None,
            dependencies: Optional[list] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if config:
            details['config'] = config
        if dependencies:
            details['dependencies'] = dependencies

        super().__init__(message, code="AGENT_INITIALIZATION_ERROR", details=details, **kwargs)


class ToolNotFoundError(AgentError):
    """工具未找到异常"""

    def __init__(
            self,
            tool_name: str,
            available_tools: Optional[list] = None,
            **kwargs
    ):
        message = f"工具 '{tool_name}' 未找到"
        details = kwargs.pop('details', {})
        details['tool_name'] = tool_name
        if available_tools:
            details['available_tools'] = available_tools

        super().__init__(message, code="TOOL_NOT_FOUND", details=details, **kwargs)


class ToolExecutionError(AgentError):
    """工具执行异常"""

    def __init__(
            self,
            message: str,
            tool_name: Optional[str] = None,
            tool_args: Optional[Dict[str, Any]] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if tool_name:
            details['tool_name'] = tool_name
        if tool_args:
            details['tool_args'] = tool_args

        super().__init__(message, code="TOOL_EXECUTION_ERROR", details=details, **kwargs)


class LLMError(AgentError):
    """LLM调用异常"""

    def __init__(
            self,
            message: str,
            model_name: Optional[str] = None,
            error_type: Optional[str] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if model_name:
            details['model_name'] = model_name
        if error_type:
            details['error_type'] = error_type

        super().__init__(message, code="LLM_ERROR", details=details, **kwargs)


class TimeoutError(AgentError):
    """超时异常"""

    def __init__(
            self,
            message: str,
            operation: Optional[str] = None,
            timeout_seconds: Optional[int] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if operation:
            details['operation'] = operation
        if timeout_seconds is not None:
            details['timeout_seconds'] = timeout_seconds

        super().__init__(message, code="TIMEOUT_ERROR", details=details, **kwargs)


class ResourceNotFoundError(AgentError):
    """资源未找到异常"""

    def __init__(
            self,
            message: str,
            resource_type: Optional[str] = None,
            resource_id: Optional[str] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id

        super().__init__(message, code="RESOURCE_NOT_FOUND", details=details, **kwargs)


class PermissionError(AgentError):
    """权限异常"""

    def __init__(
            self,
            message: str,
            operation: Optional[str] = None,
            required_permission: Optional[str] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if operation:
            details['operation'] = operation
        if required_permission:
            details['required_permission'] = required_permission

        super().__init__(message, code="PERMISSION_ERROR", details=details, **kwargs)


class RetryExhaustedError(AgentError):
    """重试耗尽异常"""

    def __init__(
            self,
            message: str,
            operation: Optional[str] = None,
            max_retries: Optional[int] = None,
            last_error: Optional[Exception] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if operation:
            details['operation'] = operation
        if max_retries is not None:
            details['max_retries'] = max_retries
        if last_error:
            details['last_error'] = str(last_error)
            details['last_error_type'] = type(last_error).__name__

        super().__init__(message, code="RETRY_EXHAUSTED", details=details, **kwargs)


class InvalidStateError(AgentError):
    """无效状态异常"""

    def __init__(
            self,
            message: str,
            current_state: Optional[str] = None,
            expected_states: Optional[list] = None,
            **kwargs
    ):
        details = kwargs.pop('details', {})
        if current_state:
            details['current_state'] = current_state
        if expected_states:
            details['expected_states'] = expected_states

        super().__init__(message, code="INVALID_STATE", details=details, **kwargs)


class AgentStateError(AgentError):
    """Agent状态相关异常"""
    pass


class AgentTemplateError(AgentError):
    """Agent模板相关异常"""
    pass


class AgentProcessingError(AgentError):
    """Agent处理过程异常"""
    pass
