"""
智能体状态枚举
定义智能体的生命周期状态 - 运行时状态管理
"""

from enum import Enum

class AgentState(Enum):
    """智能体状态枚举"""
    
    # 基础状态
    IDLE = "idle"           # 空闲状态，等待任务
    EXECUTING = "executing" # 执行中，处理任务
    PAUSED = "paused"       # 暂停状态
    ERROR = "error"         # 错误状态
    PROCESSING = "processing" # 处理消息中
    
    # 高级状态（用于复杂智能体）
    THINKING = "thinking"   # 思考中（Reflection模式）
    PLANNING = "planning"   # 规划中（Plan-Solve模式）
    REFLECTING = "reflecting" # 反思中（Reflection模式）
    
    # 系统状态
    INITIALIZING = "initializing" # 初始化中
    CLOSING = "closing"         # 正在关闭中
    CLOSED = "closed"           # 已关闭
    MAINTENANCE = "maintenance"   # 维护中
    
    def is_active(self) -> bool:
        """检查是否为活跃状态"""
        return self in [
            AgentState.EXECUTING,
            AgentState.PROCESSING,
            AgentState.THINKING,
            AgentState.PLANNING,
            AgentState.REFLECTING,
            AgentState.INITIALIZING
        ]

    def can_accept_task(self) -> bool:
        """检查是否可以接受新任务"""
        return self in [
            AgentState.IDLE,
            AgentState.PAUSED
        ]
    
    def is_error_state(self) -> bool:
        """检查是否为错误状态"""
        return self == AgentState.ERROR
    
    @classmethod
    def from_string(cls, state_str: str) -> 'AgentState':
        """从字符串转换为枚举"""
        try:
            return cls(state_str.lower())
        except ValueError:
            raise ValueError(f"无效的智能体状态: {state_str}")
    
    def __str__(self) -> str:
        return self.value