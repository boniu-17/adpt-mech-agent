"""
系统配置模块
统一管理所有系统级配置，通过YAML文件配置
"""

import os
from pathlib import Path
from typing import Dict, Any

import yaml


class SystemConfig:
    """系统配置管理器"""

    _instance = None
    _config_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        """加载配置文件"""
        # 加载主配置文件
        main_config_path = Path(__file__).parent / "config.yaml"

        if main_config_path.exists():
            with open(main_config_path, 'r', encoding='utf-8') as f:
                cls._config_data = yaml.safe_load(f) or {}
        else:
            # 如果主配置文件不存在，使用默认配置
            cls._config_data = cls._get_default_config()

        # 环境变量覆盖配置
        cls._apply_environment_overrides()

    @staticmethod
    def _merge_configs(base: Dict[str, Any], update: Dict[str, Any]):
        """深度合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                SystemConfig._merge_configs(base[key], value)
            else:
                base[key] = value

    @classmethod
    def _apply_environment_overrides(cls):
        """应用环境变量覆盖配置"""
        for key in os.environ:
            if key.startswith('CONFIG_'):
                # 转换 CONFIG_SECTION_SUBSECTION_KEY 格式为 section.subsection.key
                config_key = key[7:].lower().replace('_', '.')
                value = os.environ[key]
                cls._set_nested_value(cls._config_data, config_key, value)

    @staticmethod
    def _set_nested_value(config_dict: Dict[str, Any], key_path: str, value: Any):
        """设置嵌套字典值"""
        keys = key_path.split('.')
        current = config_dict

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # 类型转换
        last_key = keys[-1]
        if isinstance(current.get(last_key), bool):
            value = value.lower() in ('true', '1', 'yes')
        elif isinstance(current.get(last_key), int):
            try:
                value = int(value)
            except ValueError:
                pass
        elif isinstance(current.get(last_key), float):
            try:
                value = float(value)
            except ValueError:
                pass

        current[last_key] = value

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """从YAML文件获取默认配置"""
        default_config_path = Path(__file__).parent / "default_config.yaml"
        
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            # 如果默认配置文件也不存在，返回最小配置
            return {
                'system': {
                    'environment': 'development',
                    'debug': True,
                    'log_level': 'INFO'
                },
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0
                },
                'database': {
                    'dialect': 'sqlite',
                    'database': 'adpt_mech.db'
                },
                'llm': {
                    'provider': 'openai',
                    'model': 'gpt-3.5-turbo'
                }
            }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return self.get('redis', {})

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get('database', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})

    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return self.get('storage', {})

    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.get('api', {})

    def get_knowledge_config(self) -> Dict[str, Any]:
        """获取知识管理配置"""
        return self.get('knowledge', {})

    def get_agents_config(self) -> Dict[str, Any]:
        """获取智能体配置"""
        return self.get('agents', {})

    def reload(self):
        """重新加载配置"""
        self._load_config()

    def validate(self) -> bool:
        """验证配置有效性"""
        # 系统配置验证
        system_config = self.get('system', {})
        if system_config.get('environment') not in ['development', 'production', 'test']:
            raise ValueError("环境配置必须是 development、production 或 test")

        # Redis配置验证
        redis_config = self.get_redis_config()
        if not redis_config.get('host'):
            raise ValueError("Redis主机地址不能为空")
        if not (1 <= redis_config.get('port', 0) <= 65535):
            raise ValueError("Redis端口必须在1-65535之间")

        # 数据库配置验证
        db_config = self.get_database_config()
        if db_config.get('dialect') not in ['sqlite', 'mysql', 'postgresql']:
            raise ValueError("不支持的数据库方言")

        # LLM配置验证
        llm_config = self.get('llm', {})
        if not llm_config.get('provider'):
            raise ValueError("LLM提供商不能为空")

        # API配置验证
        api_config = self.get('api', {})
        if not (1 <= api_config.get('port', 0) <= 65535):
            raise ValueError("API端口必须在1-65535之间")

        return True


# 全局配置实例
config = SystemConfig()

__all__ = ['SystemConfig', 'config']
