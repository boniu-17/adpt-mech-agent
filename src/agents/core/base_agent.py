import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from src.agents.enum.run_time_state import RuntimeState

logger = logging.getLogger(__name__)


class AgentMetrics:
    """Agent 级统一指标（协议级，不掺业务）"""

    __slots__ = ("total_calls", "total_errors", "total_latency")

    def __init__(self):
        self.total_calls: int = 0
        self.total_errors: int = 0
        self.total_latency: float = 0.0


class BaseAgent(ABC):
    """
    BaseAgent = Agent 的宪法层

    负责：
    - 生命周期
    - 状态机
    - 并发安全
    - 统一执行入口
    - 指标采集

    不负责：
    - prompt
    - LLM
    - tool
    - domain logic
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id

        self.run_time_state: RuntimeState = RuntimeState.IDLE
        self._lock = asyncio.Lock()
        self._closed = False

        self.metrics = AgentMetrics()

    # ========= 对外统一入口（不可 override） =========

    async def process(self, input_data: Any, **kwargs) -> Any:
        """
        非流式处理入口
        """
        return await self._run(input_data, stream=False, **kwargs)

    async def process_stream(
            self, input_data: Any, **kwargs
    ) -> AsyncGenerator[Any, None]:
        """
        流式处理入口
        """
        result = await self._run(input_data, stream=True, **kwargs)
        async for chunk in result:
            yield chunk

    # ========= 核心调度逻辑（框架铁律） =========

    async def _run(
            self,
            input_data: Any,
            *,
            stream: bool,
            **kwargs,
    ):
        if self._closed:
            raise RuntimeError(f"Agent {self.agent_id} is closed")

        async with self._lock:
            self._enter_running()
            start_time = time.monotonic()

            try:
                self.metrics.total_calls += 1

                result = await self._process(
                    input_data,
                    stream=stream,
                    **kwargs,
                )
                return result

            except Exception as e:
                self.metrics.total_errors += 1
                self.run_time_state = RuntimeState.ERROR
                logger.exception(
                    "Agent %s processing failed", self.agent_id
                )
                raise

            finally:
                elapsed = time.monotonic() - start_time
                self.metrics.total_latency += elapsed
                if self.run_time_state != RuntimeState.CLOSED:
                    self.run_time_state = RuntimeState.IDLE

    # ========= 子类唯一需要实现的方法 =========

    @abstractmethod
    async def _process(
            self,
            input_data: Any,
            *,
            stream: bool,
            **kwargs,
    ):
        """
        子类唯一实现点：

        - stream=False：返回最终结果
        - stream=True ：返回 AsyncGenerator
        """
        raise NotImplementedError

    # ========= 生命周期 =========

    async def close(self):
        if self._closed:
            return
        self._closed = True
        self.run_time_state = RuntimeState.CLOSED
        await self._on_close()

    async def _on_close(self):
        """
        子类可选 override，用于资源释放
        """
        pass

    # ========= 状态辅助 =========

    def _enter_running(self):
        if self.run_time_state == RuntimeState.CLOSED:
            raise RuntimeError("Agent already closed")
        self.run_time_state = RuntimeState.RUNNING

    # ========= 健康检查 =========

    def health_check(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "state": self.run_time_state.value,
            "total_calls": self.metrics.total_calls,
            "total_errors": self.metrics.total_errors,
            "total_latency": round(self.metrics.total_latency, 4),
        }

# """
# Agent基类定义 - 优化版本（使用独立的TemplateManager）
# """
#
# import asyncio
# import logging
# from abc import ABC, abstractmethod
# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional, TypeVar, Generic, AsyncGenerator, Dict, Any
#
# from src.agents.DTO.agent_full_config import AgentFullConfig
# from src.agents.core.base_llm import BaseLLM
# from src.agents.core.base_message import Message
# from src.agents.enum.agent_state import AgentState
# from src.agents.models import AgentConfig, PromptTemplate
# from src.shared.exceptions import AgentError, AgentInitializationError
# from src.shared.exceptions.agent_errors import AgentStateError, AgentProcessingError
#
# logger = logging.getLogger(__name__)
#
# # 类型变量，用于泛型约束
# T = TypeVar('T')  # 输入类型
# R = TypeVar('R')  # 输出类型
#
#
# # ==================== 性能指标类 ====================
#
# @dataclass
# class AgentMetrics:
#     """Agent性能指标"""
#     instance_id: str
#     state: AgentState
#     is_initialized: bool
#     template_count: int
#     created_at: datetime
#     last_processed_at: Optional[datetime] = None
#     processing_count: int = 0
#     error_count: int = 0
#
#
# class BaseAgent(ABC, Generic[T, R]):
#     """
#     智能体抽象基类 - 优化版本（使用独立的TemplateManager）
#     """
#
#     def __init__(self, instance_id: str, config: AgentFullConfig, llm: BaseLLM):
#         """
#         初始化Agent实例
#         """
#         if not config:
#             raise AgentError("Config cannot be None")
#         if not llm:
#             raise AgentError("LLM cannot be None")
#
#         # 初始基本属性
#         self.instance_id = instance_id
#         self.session_id = None
#         self.config = config
#         self.llm = llm
#         self.state = AgentState.IDLE
#
#         # 延迟导入TemplateManager以避免循环依赖
#         from src.managers import TemplateManager
#         self.template_manager = TemplateManager()
#
#         self.is_initialized = False
#
#         # 性能监控相关
#         self.created_at = datetime.now()
#         self.last_processed_at = None
#         self.processing_count = 0
#         self.error_count = 0
#
#         # 并发控制
#         self._initialization_lock = asyncio.Lock()
#         self._processing_lock = asyncio.Lock()
#
#         logger.debug(f"Agent实例已创建: {instance_id} ({config.agent_config.name})")
#
#     async def initialize(self, full_config: AgentFullConfig, **kwargs) -> bool:
#         """
#         初始化Agent
#         """
#         async with self._initialization_lock:
#             if self.is_initialized:
#                 logger.warning(f"Agent {self.instance_id} 已经初始化过")
#                 return True
#
#             try:
#                 # 1. 验证配置
#                 self._validate_config(full_config)
#
#                 # 2. 初始化模板
#                 success = self._initialize_templates(full_config)
#                 if not success:
#                     logger.error(f"Agent模板初始化失败: {self.instance_id}")
#                     return False
#
#                 # 3. 初始化LLM（如果支持）
#                 if hasattr(self.llm, 'initialize'):
#                     try:
#                         await self.llm.initialize()
#                     except Exception as e:
#                         logger.warning(f"LLM初始化失败但继续: {e}")
#
#                 # 4. 调用子类自定义初始化
#                 await self._custom_initialize(**kwargs)
#
#                 self.is_initialized = True
#                 logger.info(f"Agent初始化成功: {self.instance_id}")
#                 return True
#
#             except Exception as e:
#                 logger.error(f"Agent初始化失败 {self.instance_id}: {e}", exc_info=True)
#                 self.error_count += 1
#                 return False
#
#     from typing import Optional
#
#     @staticmethod
#     def _validate_config(full_config: AgentFullConfig | AgentConfig):
#         """
#         验证配置完整性 - 简洁版本
#         """
#         if not full_config:
#             raise AgentInitializationError("Agent配置不能为空")
#
#         # 检查是否有角色定义模板
#         has_role_definition = BaseAgent._has_required_template(full_config, 'role_definition')
#
#         if not has_role_definition:
#             logger.warning("Agent配置缺少必需的'角色定义'模板")
#
#         return has_role_definition
#
#     @staticmethod
#     def _has_required_template(full_config: AgentFullConfig | AgentConfig, template_key: str) -> bool:
#         """检查是否包含指定模板"""
#         template = BaseAgent._extract_template(full_config, template_key)
#         return template is not None
#
#     @staticmethod
#     def _extract_template(full_config: AgentFullConfig | AgentConfig, template_key: str) -> Optional[dict]:
#         """提取指定模板"""
#         # 获取模板数据
#         templates_data = None
#
#         if isinstance(full_config, AgentFullConfig):
#             # 从AgentFullConfig获取
#             if hasattr(full_config, 'prompt_templates') and full_config.prompt_templates:
#                 templates_data = full_config.prompt_templates
#             elif (hasattr(full_config, 'agent_config') and
#                   hasattr(full_config.agent_config, 'extra_params')):
#                 extra_params = full_config.agent_config.extra_params
#                 if extra_params and 'prompt_templates' in extra_params:
#                     templates_data = extra_params['prompt_templates']
#
#         elif isinstance(full_config, AgentConfig):
#             # 从AgentConfig获取
#             if hasattr(full_config, 'extra_params') and full_config.extra_params:
#                 extra_params = full_config.extra_params
#                 if 'prompt_templates' in extra_params:
#                     templates_data = extra_params['prompt_templates']
#
#         # 提取指定模板
#         if templates_data:
#             if isinstance(templates_data, dict):
#                 return templates_data.get(template_key)
#             elif hasattr(templates_data, '__dict__'):
#                 return getattr(templates_data, template_key, None)
#
#         return None
#
#     def _initialize_templates(self, full_config: AgentFullConfig | AgentConfig) -> bool:
#         """
#         初始化模板 - 简洁版本
#         """
#         # 定义要加载的模板
#         TEMPLATES_TO_LOAD = [
#             ('role_definition', '角色定义', True),
#             ('reasoning_framework', '推理框架', False),
#             ('retrieval_strategy', '检索策略', False),
#             ('safety_policy', '安全策略', False),
#             ('process_guide', '流程指导', False),
#         ]
#
#         loaded_count = 0
#
#         for template_key, template_name, is_required in TEMPLATES_TO_LOAD:
#             try:
#                 # 提取模板数据
#                 template_data = self._extract_template(full_config, template_key)
#
#                 if not template_data:
#                     if is_required:
#                         logger.error(f"缺少必需模板: {template_name}")
#                         return False
#                     continue
#
#                 # 创建并加载模板
#                 prompt_template = self._create_prompt_template(template_data, template_name)
#                 if prompt_template:
#                     self.template_manager.add_template(template_name, prompt_template)
#                     loaded_count += 1
#                     logger.debug(f"加载模板: {template_name}")
#                 elif is_required:
#                     logger.error(f"无法创建必需模板: {template_name}")
#                     return False
#
#             except Exception as e:
#                 logger.warning(f"加载模板'{template_name}'失败: {e}")
#                 if is_required:
#                     return False
#
#         # 最终验证
#         if loaded_count > 0:
#             logger.info(f"成功加载 {loaded_count} 个模板")
#             return self.template_manager.validate_required_templates()
#
#         return False
#
#     def _create_prompt_template(self, template_data, template_name: str) -> Optional[PromptTemplate]:
#         """创建PromptTemplate对象（支持多种格式）"""
#         if isinstance(template_data, PromptTemplate):
#             return template_data
#
#         if isinstance(template_data, dict):
#             return self._create_prompt_template_from_dict(template_data, template_name)
#
#         # 尝试其他格式
#         try:
#             content = str(template_data).strip()
#             if content:
#                 return PromptTemplate(
#                     name=template_name,
#                     template=content,
#                     description=f"{template_name}模板"
#                 )
#         except:
#             pass
#
#         return None
#
#     # ==================== 核心抽象接口 ====================
#
#     @abstractmethod
#     async def process(self, input_data: T, **kwargs) -> R:
#         """处理输入并返回结果 - 同步版（子类必须实现）"""
#         pass
#
#     @abstractmethod
#     async def process_stream(self, input_data: T, **kwargs) -> AsyncGenerator[str, None]:
#         """
#         流式处理：先异步准备，再返回生成器
#         支持并行创建多个处理器
#         """
#         pass
#
#     # ==================== 模板管理代理方法 ====================
#
#     def format_prompt(self, template_name: str, **kwargs) -> str:
#         """
#         格式化prompt模板 - 代理到TemplateManager
#         """
#         return self.template_manager.format_prompt(template_name, **kwargs)
#
#     def build_full_prompt(self, user_input: str, include_templates: Optional[list] = None) -> str:
#         """
#         构建完整prompt - 代理到TemplateManager
#         """
#         return self.template_manager.build_full_prompt(user_input, include_templates)
#
#     def add_template(self, name: str, template: PromptTemplate):
#         """添加PromptTemplate对象 - 代理到TemplateManager"""
#         self.template_manager.add_template(name, template)
#
#     def add_template_from_dict(self, name: str, template_dict: dict):
#         """从字典添加模板 - 代理到TemplateManager"""
#         self.template_manager.add_template_from_dict(name, template_dict)
#
#     def add_template_from_string(self, name: str, template_string: str):
#         """从字符串添加模板 - 代理到TemplateManager"""
#         self.template_manager.add_template_from_string(name, template_string)
#
#     def get_template(self, name: str) -> Optional[PromptTemplate]:
#         """获取指定名称的模板 - 代理到TemplateManager"""
#         return self.template_manager.get_template(name)
#
#     def render_template(self, template_name: str, **kwargs) -> str:
#         """渲染指定模板 - 代理到TemplateManager"""
#         return self.template_manager.render_template(template_name, **kwargs)
#
#     def list_templates(self, include_stats: bool = True) -> Dict[str, Dict[str, Any]]:
#         """列出所有模板的详细信息 - 代理到TemplateManager"""
#         return self.template_manager.list_templates(include_stats)
#
#     def validate_template_variables(self, template_name: str, **kwargs) -> bool:
#         """验证模板变量是否匹配 - 代理到TemplateManager"""
#         return self.template_manager.validate_template_variables(template_name, **kwargs)
#
#     # ==================== 新增的模板管理便捷方法 ====================
#
#     def get_template_stats(self, template_name: str):
#         """获取模板统计信息"""
#         return self.template_manager.get_template_stats(template_name)
#
#     def clear_templates(self):
#         """清空所有模板"""
#         self.template_manager.clear_templates()
#
#     def remove_template(self, name: str) -> bool:
#         """删除指定模板"""
#         return self.template_manager.remove_template(name)
#
#     def export_templates(self) -> Dict[str, dict]:
#         """导出所有模板为字典格式"""
#         return self.template_manager.export_templates()
#
#     def import_templates(self, templates_dict: Dict[str, dict]) -> int:
#         """从字典导入模板"""
#         return self.template_manager.import_templates(templates_dict)
#
#     # ==================== 消息处理接口 ====================
#
#     async def _pre_process(self, input_data: T, **kwargs) -> T:
#         """预处理钩子 - 子类可覆盖"""
#         return input_data
#
#     async def _post_process(self, output_data: R, **kwargs) -> R:
#         """后处理钩子 - 子类可覆盖"""
#         return output_data
#
#     async def _custom_initialize(self, **kwargs):
#         """自定义初始化钩子 - 子类可覆盖"""
#         pass
#
#     # ==================== 状态管理 ====================
#
#     def get_state(self) -> AgentState:
#         """获取当前Agent状态"""
#         return self.state
#
#     def set_state(self, state: AgentState):
#         """
#         设置Agent状态 - 严格版本
#         """
#         if not isinstance(state, AgentState):
#             raise TypeError(f"Expected AgentState, got {type(state)}")
#
#         # 定义合法的状态转换
#         valid_transitions = {
#             AgentState.IDLE: [AgentState.PROCESSING, AgentState.CLOSING, AgentState.CLOSED],
#             AgentState.PROCESSING: [AgentState.IDLE, AgentState.CLOSING, AgentState.CLOSED],
#             AgentState.CLOSING: [AgentState.CLOSED],
#             AgentState.CLOSED: []  # CLOSED是终态
#         }
#
#         # 检查转换是否合法
#         allowed_transitions = valid_transitions.get(self.state, [])
#         if state not in allowed_transitions:
#             raise AgentStateError(
#                 f"无效的状态转换: {self.state.value} -> {state.value}。"
#                 f"允许的转换: {[s.value for s in allowed_transitions]}"
#             )
#
#         old_state = self.state
#         self.state = state
#
#         # 记录重要的状态转换
#         if old_state != state:
#             level = logging.INFO if state in [AgentState.CLOSING, AgentState.CLOSED] else logging.DEBUG
#             logger.log(level, f"Agent状态变更: {old_state.value} -> {state.value}")
#
#     # ==================== 性能监控 ====================
#
#     def get_metrics(self) -> AgentMetrics:
#         """获取Agent性能指标"""
#         return AgentMetrics(
#             instance_id=self.instance_id,
#             state=self.state,
#             is_initialized=self.is_initialized,
#             template_count=len(self.template_manager.templates),
#             created_at=self.created_at,
#             last_processed_at=self.last_processed_at,
#             processing_count=self.processing_count,
#             error_count=self.error_count
#         )
#
#     def get_status_report(self) -> Dict[str, Any]:
#         """获取状态报告"""
#         metrics = self.get_metrics()
#
#         # 获取模板统计
#         template_stats = {}
#         for name in self.template_manager.templates:
#             stats = self.template_manager.get_template_stats(name)
#             if stats:
#                 template_stats[name] = {
#                     "render_count": stats.render_count,
#                     "last_rendered_at": stats.last_rendered_at
#                 }
#
#         return {
#             "instance_id": metrics.instance_id,
#             "agent_name": self.config.agent_config.name,
#             "state": metrics.state.value,
#             "is_initialized": metrics.is_initialized,
#             "template_count": metrics.template_count,
#             "template_stats": template_stats,  # 新增模板统计
#             "processing_count": metrics.processing_count,
#             "error_count": metrics.error_count,
#             "created_at": metrics.created_at.isoformat(),
#             "last_processed_at": metrics.last_processed_at.isoformat() if metrics.last_processed_at else None,
#             "age_seconds": (datetime.now() - metrics.created_at).total_seconds(),
#             "llm_info": self._get_llm_info()
#         }
#
#     def _get_llm_info(self) -> Dict[str, Any]:
#         """获取LLM信息"""
#         info = {
#             "llm_type": type(self.llm).__name__,
#             "has_health_check": hasattr(self.llm, 'health_check'),
#             "has_initialize": hasattr(self.llm, 'initialize'),
#         }
#
#         # 尝试获取更多LLM信息
#         try:
#             if hasattr(self.llm, 'get_info'):
#                 llm_info = self.llm.get_info()
#                 info.update(llm_info)
#         except Exception:
#             pass
#
#         return info
#
#     async def health_check(self) -> Dict[str, Any]:
#         """健康检查"""
#         checks = {
#             "agent_state": self.state != AgentState.CLOSED,
#             "agent_initialized": self.is_initialized,
#             "templates_loaded": len(self.template_manager.templates) > 0,
#             "llm_available": True,
#             "overall": True
#         }
#
#         try:
#             # 检查LLM
#             if hasattr(self.llm, 'health_check'):
#                 llm_health = await self.llm.health_check()
#                 checks["llm_available"] = bool(llm_health)
#
#             # 检查必需模板
#             if not self.template_manager.validate_required_templates():
#                 checks["essential_templates"] = False
#                 checks["overall"] = False
#             else:
#                 checks["essential_templates"] = True
#
#             # 检查状态
#             if self.state == AgentState.CLOSED:
#                 checks["overall"] = False
#
#         except Exception as e:
#             logger.error(f"健康检查失败: {e}")
#             checks["llm_available"] = False
#             checks["overall"] = False
#
#         checks["all_passed"] = all(checks.values())
#         return checks
#
#     # ==================== 资源管理 ====================
#
#     async def close(self):
#         """
#         关闭Agent，释放资源 - 增强版本
#         """
#         if self.state == AgentState.CLOSED:
#             return
#
#         old_state = self.state
#         self.set_state(AgentState.CLOSING)
#
#         try:
#             # 关闭LLM
#             if hasattr(self.llm, 'close'):
#                 try:
#                     if asyncio.iscoroutinefunction(self.llm.close):
#                         await self.llm.close()
#                     else:
#                         self.llm.close()
#                     logger.debug("LLM关闭成功")
#                 except Exception as e:
#                     logger.warning(f"关闭LLM时出错: {e}")
#
#             # 清理模板管理器
#             self.template_manager.clear_templates()
#             self.is_initialized = False
#
#             logger.info(f"Agent资源已释放: {self.instance_id}")
#
#         finally:
#             self.state = AgentState.CLOSED
#             logger.info(f"Agent完全关闭 (之前状态: {old_state.value})")
#
#     def get_config(self) -> AgentFullConfig:
#         """获取Agent配置对象"""
#         return self.config
#
#     def get_llm(self) -> BaseLLM:
#         """获取LLM实例"""
#         return self.llm
#
#     # ==================== 上下文管理器 ====================
#
#     async def __aenter__(self):
#         """异步上下文管理器入口"""
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         """异步上下文管理器出口"""
#         await self.close()
