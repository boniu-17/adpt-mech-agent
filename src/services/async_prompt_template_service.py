# """
# 异步Prompt模板服务
# 提供Prompt模板的异步CRUD操作和渲染功能
# """
#
# from typing import Dict, Any, List, Optional
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.agents.prompts.prompt_template import PromptTemplate
# from src.agents.repositories.base_repository import BaseRepository
#
# class AsyncPromptTemplateService:
#     """异步Prompt模板服务"""
#
#     def __init__(self, session: AsyncSession):
#         self.repository = BaseRepository(session, PromptTemplate)
#
#     async def create_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
#         """创建新的Prompt模板"""
#         # 检查名称是否已存在
#         existing = await self.repository.get_by(name=template_data['name'])
#         if existing:
#             raise ValueError(f"模板名称 '{template_data['name']}' 已存在")
#
#         template = PromptTemplate(**template_data)
#         return await self.repository.create(**template_data)
#
#     async def get_template(self, template_id: int) -> Optional[PromptTemplate]:
#         """根据ID获取模板"""
#         return await self.repository.get(template_id)
#
#     async def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
#         """根据名称获取模板"""
#         return await self.repository.get_by(name=name)
#
#     async def get_active_templates(self, category: str = None, agent_type: str = None) -> List[PromptTemplate]:
#         """获取活跃的模板列表"""
#         filters = [PromptTemplate.is_active == True]
#
#         if category:
#             filters.append(PromptTemplate.category == category)
#
#         if agent_type:
#             filters.append(PromptTemplate.agent_type == agent_type)
#
#         return await self.repository.list(filters=filters)
#
#     async def update_template(self, template_id: int, update_data: Dict[str, Any]) -> Optional[PromptTemplate]:
#         """更新模板"""
#         return await self.repository.update(template_id, **update_data)
#
#     async def delete_template(self, template_id: int) -> bool:
#         """删除模板"""
#         return await self.repository.delete(template_id)