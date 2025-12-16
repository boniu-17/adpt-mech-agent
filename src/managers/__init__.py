"""
配置管理器模块
"""

from .cache_manager import UnifiedCacheManager, get_cache_manager
from .template_manager import TemplateManager

__all__ = [
    'TemplateManager',
    'UnifiedCacheManager',
    'get_cache_manager'
]
