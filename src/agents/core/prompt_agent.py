import logging
from abc import ABC, abstractmethod
from typing import Any, List

from src.agents.core.base_agent import BaseAgent
from src.agents.core.base_message import Message
from src.managers.template_manager import TemplateManager
from src.shared.exceptions.agent_errors import AgentTemplateError

logger = logging.getLogger(__name__)


class PromptAgent(BaseAgent, ABC):
    """
    PromptAgent = 语义层 Agent

    职责：
    - 管理 TemplateManager
    - 将 input_data → Message[]
    - 定义 prompt 的结构与顺序

    不负责：
    - LLM 调用
    - stream 细节
    - token / chunk / tool
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id)

        # Prompt 组件
        self.template_manager = TemplateManager()

        # PromptAgent 级配置
        self._initialized = False

    # ===== 生命周期钩子 =====

    async def _on_close(self):
        """
        PromptAgent 通常不需要资源释放
        """
        pass

    # ===== Prompt 组装主入口 =====

    def build_messages(self, input_data: Any, **kwargs) -> List[Message]:
        """
        PromptAgent 对外唯一职责：
        input → Message[]

        ⚠️ 不允许子类绕过这个入口
        """
        try:
            self._ensure_prompt_ready()
            return self._build_messages(input_data, **kwargs)
        except Exception as e:
            logger.exception("Prompt build failed")
            raise AgentTemplateError(str(e)) from e

    @abstractmethod
    def _build_messages(self, input_data: Any, **kwargs) -> List[Message]:
        """
        子类实现：
        - system / user / context 如何组织
        - 使用哪些模板
        """
        raise NotImplementedError

    # ===== 内部辅助 =====

    def _ensure_prompt_ready(self):
        """
        确保 PromptAgent 已完成必要初始化
        """
        if self._initialized:
            return

        if not self.template_manager.validate_required_templates():
            raise AgentTemplateError("Required prompt templates missing")

        self._initialized = True
