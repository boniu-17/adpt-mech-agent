from enum import Enum


class CognitiveState(Enum):
    """
    Agent 认知 / 逻辑状态
    用于 PromptAgent / SimpleAgent
    """

    NONE = "none"

    # 基础执行态
    PROCESSING = "processing"
    THINKING = "thinking"

    # 高级认知态
    PLANNING = "planning"
    REFLECTING = "reflecting"

    # Tool / 外部交互
    WAITING_TOOL = "waiting_tool"

    def is_active(self) -> bool:
        return self != CognitiveState.NONE
