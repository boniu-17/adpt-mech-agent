"""
Prompt模板服务
提供Prompt模板的CRUD操作和渲染功能
"""

import yaml
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.agents.prompts.prompt_template import PromptTemplate, PromptVersion
from src.agents.repositories.base_repository import BaseRepository

class PromptTemplateService:
    """Prompt模板服务"""
    
    def __init__(self, session: Session):
        from src.agents.prompts.prompt_template import PromptTemplate
        self.repository = BaseRepository(session, PromptTemplate)
    
    def create_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
        """创建新的Prompt模板"""
        # 检查名称是否已存在
        existing = self.repository.get_by(name=template_data['name'])
        if existing:
            raise ValueError(f"模板名称 '{template_data['name']}' 已存在")
        
        template = PromptTemplate(**template_data)
        return self.repository.create(template)
    
    def get_template(self, template_id: int) -> Optional[PromptTemplate]:
        """根据ID获取模板"""
        return self.repository.get_by_id(PromptTemplate, template_id)
    
    def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """根据名称获取模板"""
        return self.repository.get_by(name=name)
    
    def get_active_templates(self, category: str = None, agent_type: str = None) -> List[PromptTemplate]:
        """获取活跃的模板列表"""
        filters = [PromptTemplate.is_active == True]
        
        if category:
            filters.append(PromptTemplate.category == category)
        
        if agent_type:
            filters.append(PromptTemplate.agent_type == agent_type)
        
        return self.repository.get_all(PromptTemplate, filters=filters, order_by=PromptTemplate.priority.desc())
    
    def update_template(self, template_id: int, update_data: Dict[str, Any], updated_by: str) -> PromptTemplate:
        """更新模板 - 会创建版本记录"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板ID {template_id} 不存在")
        
        # 保存当前版本到历史记录
        version = PromptVersion(
            prompt_id=template.id,
            version=template.version,
            template=template.template,
            variables=template.variables,
            change_reason=update_data.get('change_reason', '常规更新'),
            changed_by=updated_by
        )
        self.repository.create(version)
        
        # 更新模板
        for key, value in update_data.items():
            if hasattr(template, key) and key not in ['id', 'created_at', 'created_by']:
                setattr(template, key, value)
        
        template.updated_by = updated_by
        return self.repository.update(template)
    
    def delete_template(self, template_id: int) -> bool:
        """删除模板（软删除）"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        if template.is_system:
            raise ValueError("系统内置模板不能删除")
        
        template.is_active = False
        self.repository.update(template)
        return True
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """渲染指定模板"""
        template = self.get_template_by_name(template_name)
        if not template:
            raise ValueError(f"模板 '{template_name}' 不存在")
        
        if not template.is_active:
            raise ValueError(f"模板 '{template_name}' 已被禁用")
        
        # 验证变量
        template.validate_variables(variables)
        
        # 渲染模板
        return template.render(**variables)
    
    def import_from_yaml(self, yaml_file_path: str, created_by: str = "system") -> List[PromptTemplate]:
        """从YAML文件导入模板"""
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            templates = PromptTemplate.create_from_yaml(yaml_data, created_by)
            created_templates = []
            
            for template in templates:
                # 检查是否已存在
                existing = self.get_template_by_name(template.name)
                if existing:
                    # 更新现有模板
                    update_data = {
                        'template': template.template,
                        'variables': template.variables,
                        'description': template.description,
                        'version': template.version,
                        'change_reason': f'从YAML文件导入: {yaml_file_path}'
                    }
                    updated = self.update_template(existing.id, update_data, created_by)
                    created_templates.append(updated)
                else:
                    # 创建新模板
                    created = self.repository.create(template)
                    created_templates.append(created)
            
            return created_templates
            
        except Exception as e:
            raise ValueError(f"YAML文件导入失败: {e}")
    
    def export_to_yaml(self, output_file: str, category: str = None) -> bool:
        """导出模板到YAML文件"""
        try:
            templates = self.get_active_templates(category)
            
            yaml_data = {'prompts': []}
            for template in templates:
                prompt_data = {
                    'name': template.name,
                    'version': template.version,
                    'description': template.description,
                    'template': template.content,
                    'variables': template.variables or {},
                    'category': template.category,
                    'agent_type': template.agent_type,
                    'template_type': template.template_type
                }
                yaml_data['prompts'].append(prompt_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            return True
            
        except Exception as e:
            raise ValueError(f"YAML文件导出失败: {e}")
    
    def get_version_history(self, template_id: int) -> List[PromptVersion]:
        """获取模板的版本历史"""
        return self.repository.get_all(
            PromptVersion, 
            filters=[PromptVersion.prompt_id == template_id],
            order_by=PromptVersion.created_at.desc()
        )
    
    def revert_to_version(self, template_id: int, version_id: int, reverted_by: str) -> PromptTemplate:
        """回滚到指定版本"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板ID {template_id} 不存在")
        
        version = self.repository.get_by_id(PromptVersion, version_id)
        if not version or version.prompt_id != template_id:
            raise ValueError(f"版本ID {version_id} 不存在或不属于该模板")
        
        # 回滚内容
        update_data = {
            'template': version.template,
            'variables': version.variables,
            'version': version.version,
            'change_reason': f'回滚到版本 {version.version} (ID: {version_id})'
        }
        
        return self.update_template(template_id, update_data, reverted_by)