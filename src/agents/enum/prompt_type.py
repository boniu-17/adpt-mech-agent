from enum import Enum


class PromptType(Enum):
    """Prompt类型枚举"""
    ROLE_DEFINITION = 'role_definition'  # 角色定义（必需）
    REASONING_FRAMEWORK = 'reasoning_framework'  # 推理框架
    COMMUNICATION_STYLE = 'communication_style'  # 沟通风格
    RETRIEVAL_STRATEGY = 'retrieval_strategy'  # 检索策略（关键新增）
    SAFETY_POLICY = 'safety_policy'  # 安全策略
    PROCESS_GUIDE = 'process_guide'  # 流程指导
