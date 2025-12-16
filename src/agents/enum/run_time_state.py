from enum import Enum


class RuntimeState(Enum):
    """
    Agent 运行态（系统事实）
    仅用于 BaseAgent
    """

    IDLE = "idle"  # 空闲
    RUNNING = "running"  # 正在执行
    ERROR = "error"  # 错误
    CLOSED = "closed"  # 已关闭

    def can_accept_task(self) -> bool:
        return self == RuntimeState.IDLE

    def is_terminal(self) -> bool:
        return self in (RuntimeState.ERROR, RuntimeState.CLOSED)
