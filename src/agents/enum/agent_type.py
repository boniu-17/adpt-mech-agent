from enum import Enum

class AgentType(Enum):
    """智能体类型枚举"""
    SIMPLE = "simple"
    REACT = "react"
    PLAN_SOLVE = "plan_solve"
    REFLECTION = "reflection"