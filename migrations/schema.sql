-- MySQL数据库配置中心表结构（重构版）
-- 基于智能体配置系统重构方案

CREATE DATABASE IF NOT EXISTS `agent_config_center` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `agent_config_center`;

-- 1. Prompt模板表
CREATE TABLE IF NOT EXISTS `prompt_templates`
(
    `id`             INT AUTO_INCREMENT PRIMARY KEY,
    `name`           VARCHAR(100) NOT NULL COMMENT '模板名称',
    `version`        VARCHAR(20)  NOT NULL DEFAULT '1.0.0' COMMENT '版本号',
    `template`       TEXT         NOT NULL COMMENT '模板内容',
    `description`    TEXT COMMENT '模板描述',
    `category`       VARCHAR(50)           DEFAULT 'general' COMMENT '业务分类',
    `variables`      JSON COMMENT '模板变量定义',
    -- 新增字段：Prompt类型分类
    `prompt_type`    ENUM (
        'role_definition',     -- 角色定义（必需）
        'reasoning_framework', -- 推理框架
        'communication_style', -- 沟通风格
        'retrieval_strategy',  -- 检索策略（关键新增）
        'safety_policy',       -- 安全策略
        'process_guide'        -- 流程指导
        )                         NOT NULL DEFAULT 'role_definition' COMMENT 'Prompt类型',

    `usage_guidance` TEXT COMMENT '使用指导说明',
    `is_required`    BOOLEAN               DEFAULT FALSE COMMENT '是否必需类型',
    `is_usable`      BOOLEAN               DEFAULT TRUE COMMENT '是否可用',
    `created_at`     TIMESTAMP             DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     TIMESTAMP             DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`     VARCHAR(100) COMMENT '创建者',
    `updated_by`     VARCHAR(100) COMMENT '更新者',

    UNIQUE KEY uk_name_version (`name`, `version`),
    INDEX idx_prompt_type (`prompt_type`),
    INDEX idx_category (`category`)
) ENGINE = InnoDB COMMENT ='Prompt模板表';

-- 2. LLM配置表
CREATE TABLE IF NOT EXISTS `llm_configs`
(
    `id`           INT AUTO_INCREMENT PRIMARY KEY,
    `name`         VARCHAR(100) NOT NULL UNIQUE COMMENT 'LLM配置名称',
    `llm_type`     VARCHAR(50)  NOT NULL COMMENT 'LLM类型',
    `model_name`   VARCHAR(100) NOT NULL COMMENT '模型名称',
    `temperature`  decimal  DEFAULT 0.7 COMMENT '温度参数(0-2)',
    `max_tokens`   INT      DEFAULT 2048 COMMENT '最大token数',
    `api_key`      VARCHAR(255) COMMENT 'API密钥',
    `base_url`     VARCHAR(500) COMMENT '基础URL',
    `timeout`      INT      DEFAULT 30 COMMENT '超时时间(秒)',
    `max_retries`  INT      DEFAULT 3 COMMENT '最大重试次数',
    `extra_params` JSON COMMENT '额外参数',
    `description`  TEXT COMMENT '描述信息',
    `is_usable`    BOOLEAN  DEFAULT TRUE COMMENT '是否可用',
    `created_at`   DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`   VARCHAR(100) COMMENT '创建者',
    `updated_by`   VARCHAR(100) COMMENT '更新者',

    INDEX idx_llm_id (`id`),
    INDEX idx_llm_type (`llm_type`),
    INDEX idx_model_name (`model_name`)
) ENGINE = InnoDB COMMENT ='LLM配置表';

-- 3. 智能体配置表
CREATE TABLE IF NOT EXISTS `agent_configs`
(
    `id`                     INT AUTO_INCREMENT PRIMARY KEY,
    `name`                   VARCHAR(100) NOT NULL UNIQUE COMMENT '角色模板名称',
    `agent_type`             VARCHAR(50)  NOT NULL COMMENT '智能体类型',

    -- 重构：分离Prompt职责
    `role_definition_id`     INT          NOT NULL COMMENT '角色定义ID',
    `reasoning_framework_id` INT COMMENT '推理框架ID',
    `retrieval_strategy_id`  INT COMMENT '检索策略ID',
    `safety_policy_id`       INT COMMENT '安全策略ID',
    `process_guide_id`       INT COMMENT '流程指导ID',

    -- 工具系统集成
    `enabled_tools`          JSON        DEFAULT ('[]') COMMENT '启用工具列表',
    `tool_call_strategy`     VARCHAR(50) DEFAULT 'conservative' COMMENT '工具调用策略',

    -- 保留字段
    `llm_config_id`          INT          NOT NULL COMMENT 'LLM配置ID',
    `max_iterations`         INT         DEFAULT 10 COMMENT '最大迭代次数',
    `timeout`                INT         DEFAULT 300 COMMENT '超时时间(秒)',
    `extra_params`           JSON COMMENT '额外参数',
    `description`            TEXT COMMENT '描述信息',
    `is_usable`      BOOLEAN               DEFAULT TRUE COMMENT '是否可用',

    `created_at`             DATETIME    DEFAULT CURRENT_TIMESTAMP,
    `updated_at`             DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`             VARCHAR(100) COMMENT '创建者',
    `updated_by`             VARCHAR(100) COMMENT '更新者',

    FOREIGN KEY (`role_definition_id`) REFERENCES `prompt_templates` (`id`) ON DELETE RESTRICT,
    FOREIGN KEY (`reasoning_framework_id`) REFERENCES `prompt_templates` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`retrieval_strategy_id`) REFERENCES `prompt_templates` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`safety_policy_id`) REFERENCES `prompt_templates` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`process_guide_id`) REFERENCES `prompt_templates` (`id`) ON DELETE SET NULL,
    FOREIGN KEY (`llm_config_id`) REFERENCES `llm_configs` (`id`) ON DELETE RESTRICT,

    INDEX idx_llm_id (`id`),
    INDEX idx_agent_type (`agent_type`)
) ENGINE = InnoDB COMMENT ='智能体配置表';

-- 4. 智能体Profile表（增强版）
CREATE TABLE IF NOT EXISTS `agent_profiles`
(
    `id`                     INT AUTO_INCREMENT PRIMARY KEY,
    `agent_config_id`        INT          NOT NULL COMMENT '智能体配置ID',

    -- 展示层字段
    `display_name`           VARCHAR(100) NOT NULL COMMENT '显示名称',
    `avatar_url`             VARCHAR(500) COMMENT '头像URL',
    `language`               VARCHAR(10) DEFAULT 'zh-CN' COMMENT '语言',

    -- 行为层字段
    `communication_style_id` INT COMMENT '沟通风格ID',
    `personality_tags`       JSON        DEFAULT ('[]') COMMENT '个性标签列表',

    -- 功能层字段
    `expertise_domains`      JSON COMMENT '专业领域',
    `max_context_length`     INT         DEFAULT 4000 COMMENT '最大上下文长度',

    -- 控制字段
    `is_public`              BOOLEAN     DEFAULT FALSE COMMENT '是否公开',
    `custom_metadata`        JSON COMMENT '自定义元数据',
    `is_usable`      BOOLEAN               DEFAULT TRUE COMMENT '是否可用',

    `created_at`             DATETIME    DEFAULT CURRENT_TIMESTAMP,
    `updated_at`             DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`             VARCHAR(100) COMMENT '创建者',
    `updated_by`             VARCHAR(100) COMMENT '更新者',

    FOREIGN KEY (`agent_config_id`) REFERENCES `agent_configs` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`communication_style_id`) REFERENCES `prompt_templates` (`id`) ON DELETE SET NULL,

    UNIQUE KEY uk_agent_config (`agent_config_id`),

    INDEX idx_llm_id (`id`),
    INDEX idx_agent_config_id (`agent_config_id`),
    INDEX idx_is_public (`is_public`)

) ENGINE = InnoDB COMMENT ='智能体Profile表';

-- 5. 消息配置表
CREATE TABLE IF NOT EXISTS `message_configs`
(
    `id`                INT AUTO_INCREMENT PRIMARY KEY,
    `name`              VARCHAR(255) NOT NULL COMMENT '配置名称',
    `max_history`       INT      DEFAULT 50 COMMENT '最大历史记录数',
    `truncate_length`   INT      DEFAULT 1000 COMMENT '截断长度',
    `enable_summary`    BOOLEAN  DEFAULT TRUE COMMENT '启用摘要',
    `summary_threshold` INT      DEFAULT 20 COMMENT '摘要阈值',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`        VARCHAR(100) COMMENT '创建者',
    `updated_by`        VARCHAR(100) COMMENT '更新者'
) ENGINE = InnoDB COMMENT ='消息配置表';


-- 6. 配置变更日志表
CREATE TABLE IF NOT EXISTS `config_change_logs`
(
    `id`            INT AUTO_INCREMENT PRIMARY KEY,
    `config_type`   VARCHAR(50) NOT NULL COMMENT '配置类型',
    `config_id`     INT         NOT NULL COMMENT '配置ID',
    `operation`     VARCHAR(20) NOT NULL COMMENT '操作类型',
    `old_values`    JSON COMMENT '旧值',
    `new_values`    JSON COMMENT '新值',
    `change_reason` TEXT COMMENT '变更原因',
    `ip_address`    VARCHAR(45) COMMENT 'IP地址',
    `user_agent`    VARCHAR(500) COMMENT '用户代理',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by`    VARCHAR(100) COMMENT '创建者',
    `updated_by`    VARCHAR(100) COMMENT '更新者',

    INDEX idx_config_type_id (`config_type`, `config_id`),
    INDEX idx_created_at (`created_at`)
) ENGINE = InnoDB COMMENT ='配置变更日志表';

-- 插入示例数据
-- 1. 插入LLM配置
INSERT INTO `llm_configs` (`name`, `llm_type`, `model_name`, `temperature`, `max_tokens`, `description`, `is_usable`,`api_key`)
VALUES ('openai-gpt4', 'openai', 'gpt-4-turbo', 0.7, 4096, 'OpenAI GPT-4 Turbo模型', TRUE,'your-api-key-here'),
       ('deepseek-chat', 'deepseek', 'deepseek-chat', 0.7, 4096, 'DeepSeek Chat模型',TRUE,'sk-8e7210bfe66b48b9930b496b4f363ade'),
       ('mock-llm', 'mock', 'mock-model', 0.7, 2048, '测试用Mock模型',FALSE,NULL);

-- 2. 插入Prompt模板（按类型分类）
INSERT INTO `prompt_templates` (`name`, `version`, `template`, `description`, `prompt_type`, `is_required`,
                                `usage_guidance`)
VALUES
-- 角色定义（必需）
('quantum_sales_manager_role', '1.0.0',
 '你是量子销售经理，负责企业级量子计算解决方案的销售工作。你的职责包括客户咨询、方案定制和销售跟进。你不能承诺无法实现的技术指标。',
 '量子销售经理角色定义', 'role_definition', TRUE, '此模板定义了智能体的核心身份和职责边界'),

-- 推理框架
('spin_sales_method', '1.0.0',
 '使用SPIN销售方法：\n1. 情境问题 - 了解客户现状\n2. 难点问题 - 识别痛点\n3. 暗示问题 - 放大问题影响\n4. 需求效益问题 - 提供解决方案价值',
 'SPIN销售推理框架', 'reasoning_framework', FALSE, '用于销售场景的思考框架'),

-- 沟通风格
('professional_friendly', '1.0.0',
 '请使用专业但亲切的语气与客户交流。保持积极态度，清晰表达技术概念，避免过于技术化的术语。', '专业友好沟通风格',
 'communication_style', FALSE, '适用于企业客户的沟通方式'),

-- 检索策略（关键新增）
('knowledge_retrieval_strategy', '1.0.0',
 '当需要具体数据或专业知识时：\n1. 首先尝试从对话历史中获取信息\n2. 如果信息不足，调用知识库工具查询相关文档\n3. 优先使用最新、最相关的知识源',
 '知识检索策略', 'retrieval_strategy', FALSE, '指导何时以及如何调用知识工具'),

-- 安全策略
('enterprise_safety_policy', '1.0.0',
 '安全限制：\n- 不得泄露客户敏感信息\n- 不得承诺无法实现的安全级别\n- 涉及技术细节时需明确标注为理论探讨',
 '企业安全策略', 'safety_policy', FALSE, '企业环境下的安全约束'),

-- 流程指导
('sales_process_guide', '1.0.0',
 '销售流程：\n第一天：建立信任，了解需求\n第二天：方案演示，价值呈现\n第三天：处理异议，促成合作', '销售流程指导',
 'process_guide', FALSE, '标准销售流程模板');

-- 3. 插入智能体配置
INSERT INTO `agent_configs` (`name`, `agent_type`, `role_definition_id`, `reasoning_framework_id`,
                             `retrieval_strategy_id`, `llm_config_id`, `enabled_tools`, `description`)
VALUES ('quantum_sales_manager', 'react', 1, 2, 4, 1, '[
  "knowledge_base",
  "calculator"
]', '量子销售经理智能体'),
       ('technical_assistant', 'simple', 1, NULL, 4, 2, '[
         "knowledge_base"
       ]', '技术助手智能体');

-- 4. 插入智能体Profile
INSERT INTO `agent_profiles` (`agent_config_id`, `display_name`, `communication_style_id`,
                              `personality_tags`, `expertise_domains`, `is_public`)
VALUES (1, '量子销售专家', 3, '[
  "professional",
  "friendly",
  "analytical"
]', '[
  "量子计算",
  "企业销售",
  "技术咨询"
]', TRUE),
       (2, '技术助手', 3, '[
         "helpful",
         "precise"
       ]', '[
         "编程",
         "系统架构",
         "DevOps"
       ]', FALSE);

-- 5. 插入消息配置
INSERT INTO `message_configs` (`name`, `max_history`, `truncate_length`)
VALUES ('default_config', 50, 1000),
       ('long_conversation', 100, 2000);

