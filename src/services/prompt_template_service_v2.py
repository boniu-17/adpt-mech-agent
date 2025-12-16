# """
# 重构后的Prompt模板服务
# 支持Prompt类型分类和工具调用集成
# """
#
# from typing import Dict, List, Optional, Any
# from sqlalchemy.orm import Session
# from src.agents.prompts.prompt_template import PromptTemplate, PromptType
# from src.agents.repositories.base_repository import BaseRepository
#
# class PromptTemplateServiceV2:
#     """重构后的Prompt模板服务"""
#
#     def __init__(self, session: Session):
#         self.session = session
#         self.repository = BaseRepository(session, PromptTemplate)
#
#     def get_by_type(self, prompt_type: PromptType, is_active: bool = True) -> List[PromptTemplate]:
#         """根据类型获取Prompt模板"""
#         query = self.session.query(PromptTemplate).filter(
#             PromptTemplate.prompt_type == prompt_type
#         )
#
#         if is_active:
#             query = query.filter(PromptTemplate.is_active == True)
#
#         return query.all()
#
#     def get_required_templates(self) -> List[PromptTemplate]:
#         """获取必需的Prompt模板（role_definition类型）"""
#         return self.get_by_type(PromptType.ROLE_DEFINITION, is_active=True)
#
#     def get_retrieval_strategies(self) -> List[PromptTemplate]:
#         """获取检索策略模板"""
#         return self.get_by_type(PromptType.RETRIEVAL_STRATEGY, is_active=True)
#
#     def get_communication_styles(self) -> List[PromptTemplate]:
#         """获取沟通风格模板"""
#         return self.get_by_type(PromptType.COMMUNICATION_STYLE, is_active=True)
#
#     def get_reasoning_frameworks(self) -> List[PromptTemplate]:
#         """获取推理框架模板"""
#         return self.get_by_type(PromptType.REASONING_FRAMEWORK, is_active=True)
#
#     def create_template_with_type(
#         self,
#         name: str,
#         template: str,
#         prompt_type: PromptType,
#         description: str = None,
#         category: str = "general",
#         variables: Dict[str, Any] = None,
#         usage_guidance: str = None,
#         is_required: bool = False
#     ) -> PromptTemplate:
#         """创建指定类型的Prompt模板"""
#
#         # 验证必需字段
#         if prompt_type == PromptType.ROLE_DEFINITION and not template.strip():
#             raise ValueError("角色定义模板内容不能为空")
#
#         new_template = PromptTemplate(
#             name=name,
#             template=template,
#             prompt_type=prompt_type,
#             description=description,
#             category=category,
#             variables=variables or {},
#             usage_guidance=usage_guidance,
#             is_required=is_required,
#             is_active=True
#         )
#
#         self.session.add(new_template)
#         self.session.commit()
#
#         return new_template
#
#     def create_default_retrieval_strategy(self) -> PromptTemplate:
#         """创建默认的检索策略模板"""
#         default_template = """
# 当用户的问题涉及以下情况时，请优先使用知识库工具进行检索：
#
# 1. 需要具体数据、事实信息时
# 2. 涉及专业知识、技术细节时
# 3. 需要最新信息或实时数据时
# 4. 问题中包含特定术语或概念时
#
# 检索策略：
# - 首先分析问题的核心需求
# - 提取关键检索词
# - 调用知识库工具进行检索
# - 对检索结果进行分析和整合
# - 基于检索信息给出专业回答
#
# 注意：避免在简单对话或常规咨询中过度使用检索工具。
# """
#
#         return self.create_template_with_type(
#             name="default_retrieval_strategy",
#             template=default_template,
#             prompt_type=PromptType.RETRIEVAL_STRATEGY,
#             description="默认的知识检索策略指导",
#             category="retrieval",
#             usage_guidance="适用于需要动态知识检索的智能体场景",
#             is_required=False
#         )
#
#     def create_default_role_definition(self, role_name: str, responsibilities: List[str]) -> PromptTemplate:
#         """创建默认的角色定义模板"""
#         responsibilities_text = "\n".join([f"- {resp}" for resp in responsibilities])
#
#         template = f"""你是{role_name}，你的主要职责包括：
#
# {responsibilities_text}
#
# 请基于你的专业知识和可用工具，为用户提供准确、专业的服务。"""
#
#         return self.create_template_with_type(
#             name=f"{role_name}_role_definition",
#             template=template,
#             prompt_type=PromptType.ROLE_DEFINITION,
#             description=f"{role_name}角色定义模板",
#             category="role",
#             is_required=True
#         )
#
#     def get_templates_for_agent_config(self, agent_config_id: int) -> Dict[str, Optional[PromptTemplate]]:
#         """获取智能体配置所需的所有模板"""
#         from src.agents.models.agent_config import AgentConfig
#
#         agent_config = self.session.query(AgentConfig).filter(
#             AgentConfig.id == agent_config_id
#         ).first()
#
#         if not agent_config:
#             return {}
#
#         templates = {
#             'role_definition': agent_config.role_definition,
#             'reasoning_framework': agent_config.reasoning_framework,
#             'retrieval_strategy': agent_config.retrieval_strategy,
#             'safety_policy': agent_config.safety_policy,
#             'process_guide': agent_config.process_guide
#         }
#
#         return {k: v for k, v in templates.items() if v}
#
#     def compile_agent_prompt(self, agent_config_id: int, context_vars: Dict[str, Any] = None) -> str:
#         """编译智能体的完整Prompt"""
#         templates = self.get_templates_for_agent_config(agent_config_id)
#
#         if not templates:
#             raise ValueError(f"未找到智能体配置 {agent_config_id} 的模板")
#
#         compiled_parts = []
#
#         # 1. 角色定义（必需）
#         if 'role_definition' in templates:
#             role_prompt = self._apply_variables(templates['role_definition'].template, context_vars)
#             compiled_parts.append(role_prompt)
#
#         # 2. 推理框架（可选）
#         if 'reasoning_framework' in templates:
#             reasoning_prompt = self._apply_variables(templates['reasoning_framework'].template, context_vars)
#             compiled_parts.append(f"\n思考方法：\n{reasoning_prompt}")
#
#         # 3. 检索策略（可选）
#         if 'retrieval_strategy' in templates:
#             retrieval_prompt = self._apply_variables(templates['retrieval_strategy'].template, context_vars)
#             compiled_parts.append(f"\n知识检索策略：\n{retrieval_prompt}")
#
#         # 4. 安全策略（可选）
#         if 'safety_policy' in templates:
#             safety_prompt = self._apply_variables(templates['safety_policy'].template, context_vars)
#             compiled_parts.append(f"\n安全限制：\n{safety_prompt}")
#
#         # 5. 流程指导（可选）
#         if 'process_guide' in templates:
#             process_prompt = self._apply_variables(templates['process_guide'].template, context_vars)
#             compiled_parts.append(f"\n工作流程：\n{process_prompt}")
#
#         return "\n\n".join(compiled_parts)
#
#     def _apply_variables(self, template: str, variables: Dict[str, Any] = None) -> str:
#         """应用变量到模板"""
#         if not variables:
#             return template
#
#         result = template
#         for key, value in variables.items():
#             placeholder = f"{{{key}}}"
#             result = result.replace(placeholder, str(value))
#
#         return result
#
#     def validate_template_content(self, template: PromptTemplate) -> List[str]:
#         """验证模板内容的合理性"""
#         warnings = []
#
#         # 检查内容长度
#         if len(template.template.strip()) < 10:
#             warnings.append("模板内容过短，可能无法提供有效指导")
#
#         # 检查变量定义
#         if template.variables:
#             for var_name, var_def in template.variables.items():
#                 if not isinstance(var_def, dict):
#                     warnings.append(f"变量 '{var_name}' 的定义格式不正确")
#
#         # 类型特定的验证
#         if template.prompt_type == PromptType.ROLE_DEFINITION:
#             if "你是" not in template.template and "You are" not in template.template:
#                 warnings.append("角色定义模板应包含明确的角色描述")
#
#         elif template.prompt_type == PromptType.RETRIEVAL_STRATEGY:
#             if "检索" not in template.template and "search" not in template.template.lower():
#                 warnings.append("检索策略模板应包含检索相关的指导")
#
#         return warnings