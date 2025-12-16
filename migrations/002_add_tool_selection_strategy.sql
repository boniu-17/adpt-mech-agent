-- 添加tool_selection_strategy字段到agent_configs表
ALTER TABLE agent_configs 
ADD COLUMN tool_selection_strategy VARCHAR(50) DEFAULT 'static' COMMENT '工具选择策略';