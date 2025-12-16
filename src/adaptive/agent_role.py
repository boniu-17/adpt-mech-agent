"""
Agent角色定义
"""

from enum import Enum


class AgentRole(Enum):
    """智能体角色枚举"""
    
    GENERAL = "general"
    """通用智能体"""
    
    SPECIALIST = "specialist" 
    """专业智能体"""
    
    COORDINATOR = "coordinator"
    """协调智能体"""