# 日志配置说明

## 概述

本项目使用统一的日志配置系统，支持控制台和文件日志输出，并提供了自动日志轮转和清理功能。

## 配置文件

日志配置位于 `configs/config.yaml` 文件的 `logging` 部分：

```yaml
# 日志配置
logging:
  # 基础配置
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  enable_colors: true
  
  # 文件日志配置
  file_logging:
    enabled: true
    directory: "logs"
    filename: "adpt_mech_agent.log"
    max_bytes: 10485760  # 10MB
    backup_count: 30     # 保留30个备份文件（约一个月）
    encoding: "utf-8"
    
  # 控制台日志配置
  console_logging:
    enabled: true
    level: "INFO"
    
  # 日志轮转和清理
  rotation:
    when: "midnight"     # 每天午夜轮转
    interval: 1          # 每天一次
    backup_count: 30     # 保留30天日志
    
  # 特定模块的日志级别
  loggers:
    "src.agents": "DEBUG"
    "src.knowledge": "INFO"
    "src.services": "INFO"
    "src.managers": "INFO"
```

## 核心功能

### 1. 多级别日志记录
- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 2. 双输出通道
- **控制台输出**: 带颜色显示，便于开发调试
- **文件输出**: 持久化存储，便于问题排查

### 3. 自动日志轮转
- 按时间轮转：每天午夜自动创建新的日志文件
- 按大小轮转：单个日志文件超过10MB时自动轮转
- 保留策略：最多保留30个备份文件（约一个月）

### 4. 模块化日志级别控制
可以针对不同模块设置不同的日志级别，例如：
- `src.agents`: DEBUG级别，便于调试智能体逻辑
- `src.knowledge`: INFO级别，记录知识库操作
- `src.services`: INFO级别，记录服务调用

## 使用方法

### 基本使用

```python
import logging
from src.shared.utils.log_config import init_logging

# 初始化日志系统
init_logging("configs/config.yaml")

# 获取logger
logger = logging.getLogger(__name__)

# 记录日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 在代码中使用

```python
from src.shared.utils import get_logger

# 推荐方式：使用项目提供的get_logger函数
logger = get_logger(__name__)

class MyService:
    def __init__(self):
        self.logger = get_logger(f"{__name__}.MyService")
    
    def process(self):
        self.logger.info("开始处理...")
        try:
            # 业务逻辑
            self.logger.debug("处理细节...")
        except Exception as e:
            self.logger.error(f"处理失败: {e}")
            raise
```

## 日志清理

### 手动清理

```bash
# 查看日志文件信息
python scripts/cleanup_logs.py --info

# 模拟清理（不实际删除）
python scripts/cleanup_logs.py --dry-run

# 清理超过30天的旧日志
python scripts/cleanup_logs.py

# 清理超过指定天数的日志
python scripts/cleanup_logs.py --days-to-keep 15
```

### 定时清理（推荐）

可以使用cron任务定期清理旧日志：

```bash
# 每天凌晨2点清理超过30天的旧日志
0 2 * * * cd /path/to/project && python scripts/cleanup_logs.py
```

## 测试日志配置

运行测试脚本验证日志系统：

```bash
python test_logging.py
```

## 最佳实践

1. **合理使用日志级别**
   - DEBUG: 详细的调试信息
   - INFO: 重要的业务流程信息
   - WARNING: 需要注意但不影响程序运行的情况
   - ERROR: 错误但程序可以继续运行
   - CRITICAL: 严重错误，程序无法继续运行

2. **使用有意义的日志消息**
   ```python
   # 好的示例
   logger.info(f"用户 {user_id} 登录成功")
   logger.error(f"数据库连接失败: {error}")
   
   # 不好的示例
   logger.info("处理完成")  # 太模糊
   logger.error("出错")     # 没有具体信息
   ```

3. **避免过度日志记录**
   - 生产环境使用INFO级别
   - 开发环境可以使用DEBUG级别
   - 敏感信息不要记录到日志中

4. **异常处理中的日志记录**
   ```python
   try:
       # 业务逻辑
   except SpecificException as e:
       logger.error(f"业务处理失败: {e}", exc_info=True)
       raise
   except Exception as e:
       logger.critical(f"未知错误: {e}", exc_info=True)
       raise
   ```

## 故障排除

### 常见问题

1. **日志文件未创建**
   - 检查logs目录权限
   - 确认file_logging.enabled为true

2. **日志级别不生效**
   - 检查配置文件格式
   - 确认模块名称拼写正确

3. **日志文件过大**
   - 调整max_bytes参数
   - 定期运行清理脚本

### 调试技巧

```python
# 临时启用详细日志
import logging
logging.getLogger().setLevel(logging.DEBUG)

# 查看所有活跃的logger
for name in logging.Logger.manager.loggerDict:
    logger = logging.getLogger(name)
    print(f"{name}: {logger.level}")
```