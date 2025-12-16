-- 智能体配置系统重构迁移脚本
-- 将系统从"Prompt包含知识"重构为"Prompt指导工具调用，知识动态检索"模式

-- ===========================================
-- 1. prompt_templates表新增字段
-- ===========================================

-- 创建prompt_type枚举类型
CREATE TYPE prompt_type_enum AS ENUM (
    'role_definition',      -- 角色定义（必需）
    'reasoning_framework',  -- 推理框架
    'communication_style',  -- 沟通风格
    'retrieval_strategy',   -- 检索策略（关键新增）
    'safety_policy',        -- 安全策略
    'process_guide'         -- 流程指导
);

-- 添加新字段到prompt_templates表
ALTER TABLE prompt_templates 
ADD COLUMN prompt_type prompt_type_enum NOT NULL DEFAULT 'role_definition',
ADD COLUMN usage_guidance TEXT,
ADD COLUMN is_required BOOLEAN DEFAULT FALSE;

-- ===========================================
-- 2. agent_configs表重构
-- ===========================================

-- 修改system_prompt为可选字段
ALTER TABLE agent_configs ALTER COLUMN system_prompt DROP NOT NULL;

-- 添加新的Prompt引用字段
ALTER TABLE agent_configs 
ADD COLUMN role_definition_id INTEGER REFERENCES prompt_templates(id) NOT NULL,
ADD COLUMN reasoning_framework_id INTEGER REFERENCES prompt_templates(id),
ADD COLUMN retrieval_strategy_id INTEGER REFERENCES prompt_templates(id),
ADD COLUMN safety_policy_id INTEGER REFERENCES prompt_templates(id),
ADD COLUMN process_guide_id INTEGER REFERENCES prompt_templates(id),
ADD COLUMN enabled_tools JSONB DEFAULT '[]',
ADD COLUMN tool_call_strategy VARCHAR(50) DEFAULT 'conservative';

-- 设置默认值：将现有的default_prompt_template_id复制到role_definition_id
UPDATE agent_configs 
SET role_definition_id = default_prompt_template_id 
WHERE default_prompt_template_id IS NOT NULL;

-- 对于没有default_prompt_template_id的记录，需要手动处理
-- 这里可以创建一个默认的role_definition模板并关联

-- ===========================================
-- 3. agent_profiles表增强
-- ===========================================

-- 添加新字段
ALTER TABLE agent_profiles 
ADD COLUMN communication_style_id INTEGER REFERENCES prompt_templates(id),
ADD COLUMN personality_tags JSONB DEFAULT '[]';

-- ===========================================
-- 4. 数据迁移：现有Prompt分类
-- ===========================================

-- 分析现有Prompt模板，按功能分类
-- 这里需要根据实际内容进行智能分类

-- 示例：将包含"你是"开头的模板标记为role_definition
UPDATE prompt_templates 
SET prompt_type = 'role_definition'
WHERE template LIKE '你是%' OR template LIKE 'You are%';

-- 示例：将包含"思考框架"、"分析方法"的模板标记为reasoning_framework
UPDATE prompt_templates 
SET prompt_type = 'reasoning_framework'
WHERE template LIKE '%思考框架%' OR template LIKE '%分析方法%' 
   OR template LIKE '%reasoning framework%' OR template LIKE '%analysis method%';

-- 示例：将包含"语气"、"风格"的模板标记为communication_style
UPDATE prompt_templates 
SET prompt_type = 'communication_style'
WHERE template LIKE '%语气%' OR template LIKE '%风格%' 
   OR template LIKE '%tone%' OR template LIKE '%style%';

-- 示例：将包含"检索"、"查询"的模板标记为retrieval_strategy
UPDATE prompt_templates 
SET prompt_type = 'retrieval_strategy'
WHERE template LIKE '%检索%' OR template LIKE '%查询%' 
   OR template LIKE '%retriev%' OR template LIKE '%search%';

-- 剩余的模板保持为role_definition
UPDATE prompt_templates 
SET prompt_type = 'role_definition'
WHERE prompt_type IS NULL;

-- ===========================================
-- 5. 创建索引优化查询性能
-- ===========================================

-- prompt_templates表索引
CREATE INDEX idx_prompt_templates_type ON prompt_templates(prompt_type);
CREATE INDEX idx_prompt_templates_active ON prompt_templates(is_active);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);

-- agent_configs表索引
CREATE INDEX idx_agent_configs_role_def ON agent_configs(role_definition_id);
CREATE INDEX idx_agent_configs_reasoning ON agent_configs(reasoning_framework_id);
CREATE INDEX idx_agent_configs_retrieval ON agent_configs(retrieval_strategy_id);
CREATE INDEX idx_agent_configs_active ON agent_configs(is_active);

-- agent_profiles表索引
CREATE INDEX idx_agent_profiles_comm_style ON agent_profiles(communication_style_id);
CREATE INDEX idx_agent_profiles_public ON agent_profiles(is_public);

-- ===========================================
-- 6. 创建视图方便查询
-- ===========================================

-- 智能体完整配置视图
CREATE VIEW agent_full_config_view AS
SELECT 
    ac.id,
    ac.name,
    ac.agent_type,
    ac.is_active,
    rd.name as role_definition_name,
    rf.name as reasoning_framework_name,
    rs.name as retrieval_strategy_name,
    sp.name as safety_policy_name,
    pg.name as process_guide_name,
    ap.display_name,
    ap.language,
    cs.name as communication_style_name,
    lc.model_name as llm_model
FROM agent_configs ac
LEFT JOIN prompt_templates rd ON ac.role_definition_id = rd.id
LEFT JOIN prompt_templates rf ON ac.reasoning_framework_id = rf.id
LEFT JOIN prompt_templates rs ON ac.retrieval_strategy_id = rs.id
LEFT JOIN prompt_templates sp ON ac.safety_policy_id = sp.id
LEFT JOIN prompt_templates pg ON ac.process_guide_id = pg.id
LEFT JOIN agent_profiles ap ON ac.id = ap.agent_config_id
LEFT JOIN prompt_templates cs ON ap.communication_style_id = cs.id
LEFT JOIN llm_configs lc ON ac.llm_config_id = lc.id;

-- ===========================================
-- 7. 记录迁移日志
-- ===========================================

INSERT INTO config_change_logs (
    config_type, config_id, operation, change_reason, created_by
) VALUES (
    'system', 0, 'update', '智能体配置系统重构：新增Prompt类型分类和工具调用集成', 'migration'
);

-- ===========================================
-- 迁移完成说明
-- ===========================================

COMMENT ON TABLE prompt_templates IS '重构后的Prompt模板表，支持类型分类和工具调用指导';
COMMENT ON TABLE agent_configs IS '重构后的智能体配置表，分离Prompt职责，集成工具系统';
COMMENT ON TABLE agent_profiles IS '增强的智能体Profile表，支持沟通风格和个性标签';

-- 重要提醒：在生产环境执行前请先备份数据！