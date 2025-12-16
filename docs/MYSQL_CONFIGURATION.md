# MySQL配置中心使用指南

## 概述

本项目支持使用MySQL数据库作为智能体配置的持久化存储，实现配置的统一管理和动态加载。

## 架构设计

### 存储策略
- **配置存储**: 使用MySQL进行持久化存储
- **状态存储**: 建议使用Redis + MySQL异步持久化（高频状态）
- **历史记录**: 使用MySQL存储用于分析和审计

### 表结构说明

#### 核心配置表
1. `llm_configs` - LLM配置表
2. `agent_configs` - 智能体配置表  
3. `prompt_templates` - Prompt模板表
4. `agent_profiles` - 智能体Profile表
5. `message_configs` - 消息配置表
6. `system_configs` - 系统配置表

## 快速开始

### 1. 环境准备

```bash
# 安装MySQL客户端
pip install mysql-connector-python

# 确保MySQL服务正在运行
sudo systemctl start mysql  # Linux
# 或启动MySQL服务 (Windows/macOS)
```

### 2. 数据库初始化

```sql
-- 创建数据库和表结构
mysql -u root -p < configs/database_schema.sql
```

### 3. 配置数据库连接

编辑 `configs/mysql_config.yaml`:

```yaml
# MySQL数据库配置
database:
  host: "localhost"
  port: 3306
  user: "root"
  password: "your_password"
  database: "agent_config_center"
  charset: "utf8mb4"
  pool_size: 5

# Redis配置（可选）
redis:
  enabled: false
  host: "localhost"
  port: 6379
  password: ""
  db: 0

# 存储策略
storage_strategy: "mysql_only"  # mysql_only, redis_only, hybrid
sync_strategy: "async"          # sync, async
```

### 4. 测试连接

```bash
# 测试MySQL连接
python test_mysql_connection.py

# 测试完整配置系统
python test_mysql_config.py
```

## 使用方法

### 基本配置管理

```python
from src.shared.config.unified_config_manager import UnifiedConfigManager

# 初始化配置管理器（自动检测并使用MySQL配置）
config_manager = UnifiedConfigManager()

# 获取LLM配置
llm_config = config_manager.get_llm_config("default_openai")

# 获取智能体配置
agent_config = config_manager.get_agent_config("simple_agent")

# 获取Prompt模板
prompt_template = config_manager.get_prompt_template("system_prompt")
```

### 动态配置更新

```python
# 保存新的LLM配置
from src.shared.config.schemas.llm import LLMConfig

new_llm = LLMConfig(
    llm_type="openai",
    model_name="gpt-4",
    temperature=0.8,
    max_tokens=4096
)

config_manager.save_llm_config(new_llm, "gpt4_config")
```

## 故障排除

### 常见问题

1. **MySQL连接失败**
   - 检查MySQL服务是否运行
   - 验证连接参数是否正确
   - 确认防火墙设置

2. **模块导入错误**
   ```bash
   pip install mysql-connector-python
   ```

3. **表不存在**
   ```bash
   mysql -u root -p < configs/database_schema.sql
   ```

4. **权限问题**
   ```sql
   GRANT ALL PRIVILEGES ON agent_config_center.* TO 'username'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 调试工具

```bash
# 检查数据库连接状态
python test_mysql_connection.py

# 检查配置加载
python test_mysql_config.py

# 查看数据库表结构
mysql -u root -p -e "USE agent_config_center; SHOW TABLES;"
```

## 性能优化建议

### 数据库优化

1. **索引优化**
   ```sql
   -- 为常用查询字段添加索引
   CREATE INDEX idx_agent_name ON agent_configs(name);
   CREATE INDEX idx_llm_type ON llm_configs(llm_type);
   ```

2. **连接池配置**
   ```yaml
   database:
     pool_size: 10  # 根据并发量调整
     pool_reset_session: true
   ```

3. **查询优化**
   - 使用分页查询大数据集
   - 避免SELECT *，只查询需要的字段
   - 合理使用缓存

### Redis集成（可选）

对于高频访问的配置，可以启用Redis缓存：

```yaml
redis:
  enabled: true
  host: "localhost"
  port: 6379
  ttl: 3600  # 缓存过期时间(秒)
```

## 监控和维护

### 监控指标
- 数据库连接数
- 查询响应时间
- 缓存命中率
- 配置更新频率

### 定期维护
- 清理过期配置
- 备份重要数据
- 优化表结构
- 更新索引统计信息

## 扩展开发

### 添加新的配置类型

1. 在数据库中创建新表
2. 在 `src/shared/config/` 中添加对应的配置类
3. 在 `UnifiedConfigManager` 中添加管理方法
4. 更新数据库初始化脚本

### 自定义存储策略

继承 `DatabaseManager` 或 `HybridDatabaseManager` 类，实现自定义的存储逻辑。

## 安全考虑

1. **敏感信息加密**
   - API密钥等敏感信息应加密存储
   - 使用环境变量或密钥管理服务

2. **访问控制**
   - 限制数据库访问权限
   - 使用最小权限原则

3. **审计日志**
   - 记录配置变更操作
   - 监控异常访问模式